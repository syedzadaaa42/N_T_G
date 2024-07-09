import speedtest

def measure_speed():
    try:
        st = speedtest.Speedtest()
        st.download()
        st.upload()
        results = st.results.dict()
        download_speed = f"Download speed: {results['download'] / 1_000_000:.2f} Mbps"
        upload_speed = f"Upload speed: {results['upload'] / 1_000_000:.2f} Mbps"
    except Exception as e:
        download_speed = "Speed Test Failed"
        upload_speed = str(e)
    return download_speed, upload_speed

download_speed, upload_speed = measure_speed()
print(download_speed)
print(upload_speed)


