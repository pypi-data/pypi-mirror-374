import os
import sys
import Orange.data
from AnyQt.QtWidgets import QLineEdit,QApplication
from Orange.widgets import widget
from Orange.widgets.utils.signals import Input, Output
from Orange.widgets.settings import Setting
import json


if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils import thread_management
    from Orange.widgets.orangecontrib.HLIT_dev.utils.hlit_python_api import daemonizer_with_input_output, expected_input_for_workflow, expected_output_for_workflow
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic
    from Orange.widgets.orangecontrib.HLIT_dev.remote_server_smb import convert, server_uvicorn
else:
    from orangecontrib.AAIT.utils import thread_management
    from orangecontrib.HLIT_dev.utils.hlit_python_api import daemonizer_with_input_output, expected_input_for_workflow, expected_output_for_workflow
    from orangecontrib.AAIT.utils.import_uic import uic
    from orangecontrib.HLIT_dev.remote_server_smb import convert, server_uvicorn


class OWAgentIA(widget.OWWidget):
    name = "AgentIA"
    description = "Runs daemonizer_no_input_output in a thread; passes data through."
    icon = "icons/agent.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/agent.png"
    priority = 1091
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/agent_ia.ui")
    ip_port = Setting("127.0.0.1:8000")
    key_name = Setting("")
    poll_sleep = Setting(0.3)
    want_control_area = False
    category = "AAIT - API"

    class Inputs:
        data = Input("Data", Orange.data.Table)

    class Outputs:
        data = Output("Data", Orange.data.Table)
        expected_input = Output("Expected input", Orange.data.Table)
        expected_output = Output("Expected output", Orange.data.Table)

    def __init__(self):
        super().__init__()

        self.setFixedWidth(700)
        self.setFixedHeight(300)
        uic.loadUi(self.gui, self)

        # self._token = None         # keeps last incoming token
        self.data = None
        self.thread = None
        self.autorun = True
        self.result = None

        # hard-coded server params
        self.ip_port = "127.0.0.1:8000"
        self.key_name_input = self.findChild(QLineEdit, 'KeyName')
        self.key_name_input.setPlaceholderText("Key name")
        self.key_name_input.setText(self.key_name)
        self.key_name_input.editingFinished.connect(self.update_settings)
        self.poll_sleep = 0.3
        self.post_initialized()
        self.get_expected_input_output()

    @Inputs.data
    def set_data(self, in_data):
        self.data = in_data
        if self.autorun:
            self.set_expected_input()
            self.set_expected_output()
            self.run()

    def get_expected_input_output(self):
        if not server_uvicorn.is_port_in_use("127.0.0.1", 8000):
            self.error("An error occurred you need to start server")
            return
        self.set_expected_input()
        self.set_expected_output()

    def set_expected_input(self):
        if self.key_name != "":
            data_input = []
            if 0 != expected_input_for_workflow(self.ip_port, "max", out_tab_input=data_input):
                print("erreur lors de la lecture des inputs du workflow")
            try:
                raw_str = json.loads(data_input[0])
                data_input = convert.convert_json_to_orange_data_table(raw_str[0]["data"][0])
                self.Outputs.expected_input.send(data_input)
            except Exception as e:
                print("Erreur au chargement de la lecture des entrées du workflow : ", e)
                self.Outputs.expected_input.send(None)
            return

    def set_expected_output(self):
        if self.key_name != "":
            data_output = []
            if 0 != expected_output_for_workflow(self.ip_port, "max", out_tab_output=data_output):
                print("erreur lors de la lecture des outputs du workflow")
            try:
                raw_str = json.loads(data_output[0])
                data_output = convert.convert_json_implicite_to_data_table(raw_str[0]["data"])
                self.Outputs.expected_output.send(data_output)
            except Exception as e:
                print("Erreur au chargement de la sortie du workflow : ", e)
                self.Outputs.expected_output.send(None)
            return

    def _run_daemonizer(self, in_data,
                        ip_port="127.0.0.1:8000",
                        key_name="",
                        poll_sleep=0.3):
        """Worker function executed inside the Thread."""
        out_tab_output = []
        rc = daemonizer_with_input_output(
            in_data, ip_port, key_name, temporisation=poll_sleep, out_tab_output=out_tab_output
        )
        if rc != 0:
            raise RuntimeError(f"daemonizer finished with code {rc}")
        return out_tab_output[0]

    def update_settings(self):
        self.key_name = self.key_name_input.text()
        if self.key_name != "" and self.thread is None:
            self.set_expected_input()
            self.set_expected_output()
            self.run()


    def run(self):
        # if thread is running quit
        if self.thread is not None:
            self.thread.safe_quit()

        if self.data is None:
            return

        if not server_uvicorn.is_port_in_use("127.0.0.1", 8000):
            self.error("An error occurred you need to start server")
            return

        self.error("")
        self.progressBarInit()

        self.thread = thread_management.Thread(self._run_daemonizer,self.data, self.ip_port, self.key_name, self.poll_sleep)
        self.thread.progress.connect(self.handle_progress)
        self.thread.result.connect(self.handle_result)
        self.thread.finish.connect(self.handle_finish)
        self.thread.start()

    def handle_progress(self, value: float) -> None:
        self.progressBarSet(value)

    def handle_result(self, result):
        try:
            self.result = result
            self.Outputs.data.send(result)
        except Exception as e:
            print("An error occurred when sending out_data:", e)
            self.Outputs.data.send(None)
            return

    def handle_finish(self):
        self.progressBarFinished()

    def post_initialized(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    #data = Orange.data.Table(r"C:\Users\max83\Desktop\Orange_4All_AAIT\Orange_4All_AAIT\aait_store\input_data.tab")
    w = OWAgentIA()
    w.show()
    #w.set_data(data)
    if hasattr(app, "exec"):
        app.exec()
    else:
        app.exec_()




