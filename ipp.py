from typing import Callable
import cups
from zeroconf import Zeroconf, ServiceInfo
import socket
from time import sleep

PRINTER_NAME = "BraillePrinter"
SERVER_NAME  = PRINTER_NAME.lower()
PRINTER_PATH = f"ipp://localhost/printers/{PRINTER_NAME}"
ADVIRTISE_IP = "153.106.94.188"

SPOOL_PATH   = "/var/spool/cups/"
JOB_CB = Callable[[int, bytes], None]
class PseudoPrinter:
    def __init__(self, printer_name: str, printer_path: str,
                       advirtise_ip: str, server_name: str,
                       process_job_cb: JOB_CB,
                       spool_path: str = SPOOL_PATH,
                 ) -> None:
        self.printer_name = printer_name
        self.printer_path = printer_path
        self.advirtise_ip = advirtise_ip
        self.server_name  = server_name
        self.process_job_cb = process_job_cb
        self.spool_path = spool_path

        self.conn = cups.Connection()

    def makePrinter(self) -> None:
        self.conn.addPrinter(self.printer_name, device=self.printer_path)
        self.conn.enablePrinter(self.printer_name)
        self.conn.acceptJobs(self.printer_name)

    def advirtisePrinter(self) -> None:
        service = ServiceInfo(
            "_ipp._tcp.local.",
            f"{self.printer_name}._ipp._tcp.local.",
            addresses=[socket.inet_aton(self.advirtise_ip)],
            port=631,
            properties={}, # explicitly making sure this is empty
            server=f"{self.server_name}.local."
        )
        zeroconf = Zeroconf()
        zeroconf.register_service(service)

    def __handlePrintJob(self) -> None:
        jobs = self.conn.getJobs(which_jobs = "not-completed")
        for id, job in jobs.items():
            # read the raw bytes content from the file
            # example data file spool path: /var/spool/cups/d00005-001
            # where 5 is the job id
            with open(f"{self.spool_path}/d{id:05d}-001", "rb") as job_content:
                self.process_job_cb(id, job_content.read())

    def handlePrintJobs(self) -> None:
        while True:
            self.__handlePrintJob()
            sleep(5)

    def shutdown(self) -> None:
        # TODO: finish
        pass

    def set_spool_path(self, new_spool_path: str) -> None:
        self.spool_path = new_spool_path

def process_job(id: int, content: bytes) -> None:
    print(f"Processing job {id}")
    print(content)

if __name__ == "__main__":
    braille_printer = PseudoPrinter(
        PRINTER_NAME, PRINTER_PATH,
        ADVIRTISE_IP, SERVER_NAME,
        process_job
    )

    try:
        braille_printer.makePrinter()
        print(f"Successfully added printer {PRINTER_NAME} @ {PRINTER_PATH}")
    except Exception as e:
        print(f"Failed to add printer {PRINTER_NAME}\n{e}")

    try:
        braille_printer.advirtisePrinter()
        print(f"Successfully advirtised printer {PRINTER_NAME}")
    except Exception as e:
        print(f"Failed to advirtise printer {PRINTER_NAME}\n{e}")

    try:
        # infinite loop
        braille_printer.handlePrintJobs()
    except KeyboardInterrupt:
        print(f"\n\n{PRINTER_NAME} shutting down")
        braille_printer.shutdown()
        print(f"{PRINTER_NAME} shutdown")

