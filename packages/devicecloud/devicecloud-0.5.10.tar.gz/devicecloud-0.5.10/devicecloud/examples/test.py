from devicecloud import DeviceCloud

# dc = DeviceCloud("logrotest", "")
dc = DeviceCloud(api_key_id="94c4d18159d1eca87813f7c4d4b5da61", api_key_secret="d5e2bcbcc0493a645cf741f091bb21e88edfbc642d091f61d3a0092d1afca848")
# dc = DeviceCloud()
if dc.has_valid_credentials():
    print(list(dc.devicecore.get_devices()))
else:
    print("Invalid credentials")
