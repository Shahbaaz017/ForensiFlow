# ForensiFlow
An automated digital forensics orchestration framework that streamlines evidence ingestion, triage, and reporting by integrating industry-standard CLI tools into a unified pipeline.

## Usage

1. Install dependencies:
   ```bash
   sudo apt-get update && sudo apt-get install -y libimage-exiftool-perl
   ```
2. Run analysis:
   ```bash
   python3 main.py [evidence/<evidence-file>]
   ```

   - If no argument is provided, `main.py` defaults to `evidence/valid_test.exe`.
   - The program writes a JSON report (and audit log) to `evidence_output/`.

3. Reports are saved to `evidence_output/`.

## Notes
- The main entrypoint is `main.py`.
- Workers are in `workers/`; doc worker uses ExifTool.
- The framework always runs YARA analysis, then runs the primary worker based on file type (PDF → DocWorker, EXE → CapaWorker).

