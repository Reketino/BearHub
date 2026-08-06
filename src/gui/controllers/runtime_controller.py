from PySide6.QtCore import QThread

from runtime.calibration_worker import CalibrationWorker

class RuntimeController:
    def __init__(self, window):
        self.view = window
        
    #-------- START RUNTIME --------#
        
    def start_runtime(self):
        self.view.engine.start()
        
        self.view.start_button.setEnabled(False)
        self.view.calibrate_button.setEnabled(False)
        self.view.stop_button.setEnabled(True)
        
        self.view.status.setText(
            "Runtime started."
        )
    
    #-------- STOP RUNTIME --------#
        
    def stop_runtime(self):
        self.view.engine.stop()
        
        self.view.start_button.setEnabled(True)
        self.view.calibrate_button.setEnabled(True)
        self.view.stop_button.setEnabled(False)
        
        self.view.status.setText(
            "Runtime stopped."
        )
    
    #-------- CALIBRATE G KEYS --------#
        
    def calibrate_g_keys(self):
        self.view.status.setText(
            "Starting calibration..."
        )
        
        self.view.calibrate_button.setEnabled(False)
        self.view.start_button.setEnabled(False)
        self.view.stop_button.setEnabled(False)
        
        self.view.calibration_thread = QThread()
        self.view.calibration_worker = CalibrationWorker()
        
        self.view.calibration_worker.moveToThread(
            self.view.calibration_thread
        )
        
        self.view.calibration_thread.started.connect(
            self.view.calibration_worker.run
        )
        
        self.view.calibration_worker.finished.connect(
            self.calibration_finished
        )
        
        self.view.calibration_worker.progress.connect(
            self.calibration_progress
        )
        
        self.view.calibration_worker.error.connect(
            self.calibration_failed
        )
        
        self.view.calibration_worker.finished.connect(
            self.view.calibration_thread.quit
        )
        self.view.calibration_worker.error.connect(
            self.view.calibration_thread.quit
        )
        self.view.calibration_worker.finished.connect(
            self.view.calibration_worker.deleteLater
        )
        self.view.calibration_worker.error.connect(
            self.view.calibration_worker.deleteLater
        )
        self.view.calibration_thread.finished.connect(
            self.view.calibration_thread.deleteLater
        )
        self.view.calibration_thread.finished.connect(
            self.calibration_cleanup
        )
        
        self.view.calibration_thread.start()
        
    #-------- CALIBRATION PROGRESS --------#
    
    def calibration_progress(self, key_name):
        self.view.status.setText(
            f"Press {key_name}..."
        )
        
    #-------- CALIBRATION FINISHED --------#
            
    def calibration_finished(self):
        self.view.status.setText(
            "Calibration completed."
        )
        
        self.view.calibrate_button.setEnabled(True)
        self.view.start_button.setEnabled(True)
        self.view.stop_button.setEnabled(False)
        
    #-------- CALIBRATION FAILED--------#
        
    def calibration_failed(self, message):
        self.view.status.setText(
            "Calibration failed."
        )
        
        self.view.calibrate_button.setEnabled(True)
        self.view.start_button.setEnabled(True)
        self.view.stop_button.setEnabled(False)
                
        print(
            f"Calibration error: {message}"
        )
            
    def calibration_cleanup(self):
        self.view.calibration_worker = None
        self.view.calibration_thread = None
            

        
       