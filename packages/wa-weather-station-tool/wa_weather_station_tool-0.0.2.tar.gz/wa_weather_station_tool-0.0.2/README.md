# animal_data_analysis_tools
Develop the utility tools for animal experiments data analysis for the researchers.

## WA DPIRD Weather Downloader (minimal)
- Command: `python scripts/wa_dpird_weather_downloader.py --help`
- Example: `python scripts/wa_dpird_weather_downloader.py --station 009225 --start 2024-01-01 --end 2024-01-31 --out datasets/weather_data.csv`

This minimal CLI scaffolding writes a placeholder CSV confirming arguments. Real download logic will be integrated later in `src/wa_weather_station_tool`.

### Install locally for development
- Editable install: `pip install -e .`
- Run CLI after install: `wa_dpird_weather_downloader --help`

### Build & publish to PyPI (summary)
1) Build: `python -m build` (install `build` first)
2) Upload: `twine upload dist/*` (use PyPI API token `__token__`)
See below for detailed steps.

### Detailed PyPI publish steps
1. Create PyPI account and API token (scoped to the project)
2. Install tooling: `pip install build twine`
3. Bump version in `pyproject.toml` under `[project] version`
4. Build artifacts: `python -m build` (creates `dist/*.tar.gz` & `dist/*.whl`)
5. Upload to TestPyPI (optional): `twine upload -r testpypi dist/*`
   - Then install to test: `pip install -i https://test.pypi.org/simple/ wa-weather-station-tool`
6. Upload to PyPI: `twine upload dist/*`
   - Username: `__token__`, Password: your API token
7. Verify install: `pip install wa-weather-station-tool && wa_dpird_weather_downloader --help`
