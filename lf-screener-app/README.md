# LF Screener App (MCSA PoC)

This PoC runs a parallel screener implementing the MCSA scoring algorithm.

Quick start:

1. Create a Python virtual environment and install deps:
   ```bash
   pip install -r requirements.txt
   ```
2. Fill `.env` with TradingView credentials (optional for PoC):
   ```text
   TV_USERNAME=your_username
   TV_PASSWORD=your_password
   ```
3. Run the PoC:
   ```bash
   python main.py
   ```

Reports are written to `reports/screener_output.txt` by default (check `config.yaml`).
