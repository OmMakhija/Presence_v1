import asyncio
from bleak import BleakScanner
from backend.config import Config
from backend.models import User
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BLEProximityService:
    def __init__(self):
        self.rssi_threshold = Config.BLE_RSSI_THRESHOLD

    async def scan_for_devices(self, duration=5):
        """
        Scan for nearby BLE devices using BleakScanner.
        
        Args:
            duration: Scan duration in seconds
        
        Returns:
            list: Detected devices with RSSI values
        """
        logger.info(f"Starting BLE scan for {duration} seconds...")
        try:
            devices = await BleakScanner.discover(timeout=duration)
            
            results = []
            for device in devices:
                logger.info(f"Found device: {device.name} ({device.address}) RSSI: {device.rssi}")
                results.append({
                    'address': device.address,
                    'name': device.name,
                    'rssi': device.rssi
                })
            
            logger.info(f"Scan complete. Found {len(results)} devices.")
            return results
        except Exception as e:
            logger.error(f"BLE Scan Error: {e}")
            return []

    async def check_proximity(self, user_id):
        """
        Check if a user's registered device is nearby.
        
        Args:
            user_id: User ID to check
            
        Returns:
            dict: Proximity verification result
        """
        user = User.query.get(user_id)
        if not user or not user.device_uuid:
            logger.warning(f"User {user_id} has no registered device UUID")
            return {
                'verified': False,
                'error': 'Device not registered',
                'rssi': None
            }
            
        target_address = user.device_uuid.strip().upper()
        logger.info(f"Checking proximity for user {user.name} (Target: {target_address})")
        
        devices = await self.scan_for_devices()
        
        # Check if user's device is in the scanned list
        found_device = None
        for device in devices:
            # Match by address (MAC)
            if device['address'].upper() == target_address:
                found_device = device
                break
                
        if found_device:
            rssi = found_device['rssi']
            verified = rssi >= self.rssi_threshold
            logger.info(f"Target device found! RSSI: {rssi} (Threshold: {self.rssi_threshold}) - Verified: {verified}")
            
            return {
                'verified': verified,
                'user_id': user_id,
                'rssi': rssi
            }
        
        logger.warning(f"Target device {target_address} NOT found in scan results")
        return {
            'verified': False,
            'user_id': user_id,
            'rssi': None
        }
