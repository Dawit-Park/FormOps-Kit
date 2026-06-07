# Changelog

## 0.1.1

- Added Korean workflow presets for course inquiries, client consultations, and partner settlement requests
- Improved the GUI so non-developers can choose a workflow type and compile CSV files without editing `config.json`
- Added Korean sample CSV generation from the GUI and CLI
- Added CSV decoding fallback for Korean Excel exports (`cp949`, `euc-kr`)
- Added Korean date and time parsing such as `2026년 6월 12일`, `오후 2시`, and `오전 10:30`
- Updated the release workflow to publish `v0.1.1`

## 0.1.0

- Initial local-first CSV compiler
- Markdown operation packet generation
- Basic calendar `.ics` generation
- Example config and responses
- CI workflow and tests
- Multiple real-world example workflows
- Stable calendar event UIDs for regenerated packets
- Basic local GUI for choosing CSV/config/output paths
- Windows-friendly `formops-gui.pyw` launcher
- GitHub Actions workflow for building a Windows GUI executable
- Manual GitHub Release publishing workflow for v0.1
- Fixed the Windows executable build so the bundled app includes the `formops_kit` package
