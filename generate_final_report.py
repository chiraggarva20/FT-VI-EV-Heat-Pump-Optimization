"""
generate_final_report.py
========================
Compiles report_template.html to Final_Report_IEEE_FT_VI_Heat_Pump.pdf using Chrome headless.
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT_HTML = os.path.join(HERE, "report_template.html")
OUTPUT_PDF = os.path.join(HERE, "Final_Report_IEEE_FT_VI_Heat_Pump.pdf")

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(chrome_path):
    chrome_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

cmd = [
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--no-pdf-header-footer",
    f"--print-to-pdf={OUTPUT_PDF}",
    INPUT_HTML
]

print("Executing headless Chrome PDF generation...")
res = subprocess.run(cmd, capture_output=True, text=True)

if os.path.exists(OUTPUT_PDF):
    size_kb = os.path.getsize(OUTPUT_PDF) / 1024.0
    print(f"SUCCESS: PDF generated at: {OUTPUT_PDF} ({size_kb:.1f} KB)")
else:
    print(f"ERROR: PDF generation failed:\n{res.stderr}")
