"""GDS Viewer Additions to KWeb/DoWeb."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import doweb.api.viewer as doweb_viewer
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse

from gdsfactoryplus.core.pdk import get_pdk
from gdsfactoryplus.core.shared import merge_rdb_strings

from .app import PDK, PROJECT_DIR, app, logger


@app.get("/view2")
async def view2(
    request: Request,
    file: str,
    cell: str = "",
    rdb: str = "",
    theme: Literal["light", "dark"] = "dark",
    *,
    regen_lyp: bool = False,
    move_enabled: bool = True,
) -> HTMLResponse:
    """Alternative view specifically for GDSFactory+."""
    if PROJECT_DIR is None:
        msg = "GDSFactory+ server was not started correctly."
        raise ValueError(msg)

    gds_path = Path(file).resolve()

    lyrdb_dir = PROJECT_DIR / "build" / "lyrdb"
    temp_rdb = False
    prdb = None
    if rdb:
        rdbs = [Path(p).resolve() for p in rdb.split(",")]
        logger.info(rdbs)
        if len(rdbs) == 1 and rdbs[0].is_relative_to(lyrdb_dir / "temp"):
            prdb = rdbs[0]
            temp_rdb = True  # noqa: F841
        else:
            prdb = lyrdb_dir / rdbs[0].name
            xmls = [Path(xml).read_text() for xml in rdbs]
            xml = merge_rdb_strings(*xmls)
            prdb.write_text(xml)

    layer_props = PROJECT_DIR / "build" / "lyp" / f"{PDK}.lyp"
    if regen_lyp or not layer_props.is_file():
        _pdk = get_pdk()
        layer_views = _pdk.layer_views
        if layer_views is not None:
            if isinstance(layer_views, str | Path):
                layer_props = str(Path(layer_views).resolve())
            else:
                layer_views.to_lyp(filepath=layer_props)

    try:
        fv = doweb_viewer.FileView(
            file=gds_path,
            cell=cell or None,
            layer_props=str(layer_props),
            rdb=None if not rdb else str(prdb),
        )
        resp = await doweb_viewer.file_view_static(request, fv)
    except HTTPException:
        color = "#f5f5f5" if theme == "light" else "#121317"
        return HTMLResponse(f'<body style="background-color: {color}"></body>')
    body = resp.body.decode()  # type: ignore[reportAttributeAccessIssue]
    body = _modify_body(
        body, theme, temp_rdb=False, move_enabled=move_enabled
    )  # temp_rdb)
    return HTMLResponse(body)


def _modify_body(
    body: str,
    theme: str,
    *,
    temp_rdb: bool = False,
    move_enabled: bool = True,
) -> str:
    if theme == "light":
        body = body.replace('data-bs-theme="dark"', 'data-bs-theme="light"')

    # Path to the view.js file served via the assets mount
    js_path = "/assets/js/view.js"

    body = body.replace(
        "</head>",
        f"""<style>
     [data-bs-theme=light] {{
       --bs-body-bg: #f5f5f5;
     }}
     [data-bs-theme=dark] {{
       --bs-body-bg: #121317;
     }}
   </style>
   <script src="{js_path}"></script>
   </head>""",
    )
    body = body.replace(
        "</body>",
        f"""<script>
            // Initialize the GDS viewer with configuration
            if (window.gdsViewer) {{
                gdsViewer.initializeViewer(
                    {str(temp_rdb).lower()},
                    {str(move_enabled).lower()},
                    "{theme}"
                );
                gdsViewer.setupMessageListener();
            }} else {{
                console.error('GDS Viewer JavaScript not loaded');
            }}
        </script>
        </body>""",
    )
    return body.replace(" shadow ", " shadow-none ")
