import hid
from .config import Config

# utility class for RK Color Utility
class RKCU:
    def __init__(self, vid, pid):
        self.device = self.find_kb_hid(vid, pid)
    
    def find_kb_hid(self, vid, pid):
        rk_devices = hid.enumerate(vid, pid)
        if not rk_devices:
            raise IOError("RK keyboard not found. Please check VID and PID.")

        target_interface = None
        for device_info in rk_devices:
            path = device_info['path']
            if isinstance(path, bytes):
                path_str = path.decode('utf-8', errors='ignore')
            else:
                path_str = str(path)
            
            if 'Col05' in path_str and device_info.get('usage_page', 0) == 65280:
                target_interface = device_info
                break
        
        if not target_interface:
            for device_info in rk_devices:
                if device_info.get('usage_page', 0) == 65280:
                    target_interface = device_info
                    break
        
        if not target_interface:
            raise IOError("Could not find the configuration interface (usage_page=65280) for the keyboard.")
        
        try:
            path = target_interface['path']
            h = hid.device()
            h.open_path(path)
            return h
        except Exception as e:
            raise IOError(f"Could not open the keyboard configuration interface: {e}")
    
    def apply_config(self, config: Config):
        data_to_send = config.report()
        try:
            result = self.device.send_feature_report(bytes(data_to_send))
            if result != len(data_to_send):
                raise IOError(f"Failed to send complete config. Expected {len(data_to_send)} bytes, sent {result}")
        except Exception as e:
            raise IOError(f"Failed to send config to keyboard: {e}")
        
        # Send per-key RGB buffers if they exist
        custom_buffers = config.get_custom_light_buffers()
        for buffer in custom_buffers:
            try:
                result = self.device.send_feature_report(bytes(buffer))
                if result != len(buffer):
                    raise IOError(f"Failed to send complete custom RGB buffer. Expected {len(buffer)} bytes, sent {result}")
            except Exception as e:
                raise IOError(f"Failed to send custom RGB buffer to keyboard: {e}")
    
    def close_kb(self):
        self.device.close()