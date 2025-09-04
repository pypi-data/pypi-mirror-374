import ubluetooth
import struct
import time
from micropython import const

# BLE 이벤트 상수
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTS_READ_REQUEST = const(4)

# GATT 서비스 및 특성 UUID (표준 UUID 사용)
_UART_UUID = ubluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = ubluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_RX = ubluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")

class WebBLEPeripheral:
    def __init__(self, ble, name="ESP32"):
        self._ble = ble
        self._name = name
        self._connections = set()
        self._write_callback = None
        self._read_callback = None
        
        # GATT 서비스 등록
        self._register_services()
        
        # BLE 이벤트 핸들러 설정
        self._ble.irq(self._irq)
        
        # 광고 시작
        self._advertise()
    
    def _register_services(self):
        """GATT 서비스와 특성을 등록합니다."""
        # UART 서비스 정의
        UART_SERVICE = (
            _UART_UUID,
            (
                (_UART_TX, ubluetooth.FLAG_READ | ubluetooth.FLAG_NOTIFY),
                (_UART_RX, ubluetooth.FLAG_WRITE | ubluetooth.FLAG_WRITE_NO_RESPONSE),
            ),
        )
        
        SERVICES = (UART_SERVICE,)
        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services(SERVICES)
    
    def _irq(self, event, data):
        """BLE 이벤트 핸들러"""
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
            print(f"기기 연결됨: {conn_handle}")
        
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.discard(conn_handle)
            print(f"기기 연결 해제됨: {conn_handle}")
            # 연결이 끊어지면 다시 광고 시작
            self._advertise()
        
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == self._handle_rx and self._write_callback:
                value = self._ble.gatts_read(self._handle_rx)
                try:
                    decoded_value = value.decode('utf-8')
                    self._write_callback(decoded_value)
                except:
                    self._write_callback(value)
        
        elif event == _IRQ_GATTS_READ_REQUEST:
            conn_handle, value_handle = data
            if value_handle == self._handle_tx and self._read_callback:
                data = self._read_callback()
                if data:
                    self._ble.gatts_write(self._handle_tx, data)
    
    def _advertise(self):
        """BLE 광고를 시작합니다."""
        name = self._name
        payload = bytearray()
        
        # 장치 이름 추가
        payload.extend(struct.pack("BB", len(name) + 1, 0x09))
        payload.extend(name.encode())
        
        # 서비스 UUID 추가
        payload.extend(struct.pack("BB", 17, 0x06))
        payload.extend(_UART_UUID)
        
        self._ble.gap_advertise(100, payload)
        print(f"BLE 광고 시작: {name}")
    
    def on_write(self, callback):
        """데이터 수신 시 호출될 콜백 함수를 설정합니다."""
        self._write_callback = callback
    
    def on_read(self, callback):
        """데이터 읽기 요청 시 호출될 콜백 함수를 설정합니다."""
        self._read_callback = callback
    
    def write(self, data):
        """연결된 모든 기기에 데이터를 전송합니다."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        for conn_handle in self._connections:
            try:
                self._ble.gatts_write(self._handle_tx, data)
                self._ble.gatts_notify(conn_handle, self._handle_tx)
            except Exception as e:
                print(f"데이터 전송 실패: {e}")
    
    def send(self, data):
        """write() 메서드의 별칭"""
        self.write(data)
    
    def is_connected(self):
        """연결 상태를 확인합니다."""
        return len(self._connections) > 0
    
    def disconnect_all(self):
        """모든 연결을 끊습니다."""
        for conn_handle in self._connections.copy():
            self._ble.gap_disconnect(conn_handle)
    
    def stop(self):
        """BLE 서비스를 중지합니다."""
        self.disconnect_all()
        self._ble.active(False)

