import base64
import re
from typing import Optional, Dict, Any
import requests
from bs4 import BeautifulSoup

class PresensiClient:
    """
    Client to handle login and send presence (presensi) data to https://presensi.bskap.id
    using a data URI image (data:image/png;base64,...).
    """

    def __init__(
        self,
        user_id: str,
        password: str,
        base_url: str = "https://presensi.bskap.id",
        session: Optional[requests.Session] = None,
    ) -> None:
        self.user_id = user_id
        self.password = password
        self._base_url = base_url.rstrip("/")
        self._session = session or requests.Session()
        self._token = None

    def login(self) -> None:
        """
        Perform login to presensi.bskap.id and retrieve session + CSRF _token for further requests.
        """
        # Step 1: Get CSRF _token from login page
        get_token_url = f"{self._base_url}"
        resp = self._session.get(get_token_url)
        if resp.status_code != 200:
            raise Exception(f"Failed to load {get_token_url}: {resp.status_code}")

        soup = BeautifulSoup(resp.text, "html.parser")
        token_input = soup.find("input", {"name": "_token"})
        if not token_input or not token_input.get("value"):
            raise Exception("Could not find _token input field on the page.")

        login_token = token_input["value"]

        # Step 2: Post to login endpoint
        post_url = f"{self._base_url}/login"
        payload = {
            "_token": login_token,
            "id_user": self.user_id,
            "password": self.password
        }
        resp_post = self._session.post(post_url, data=payload)
        if resp_post.status_code != 200:
            raise Exception(f"Login failed: {resp_post.status_code} {resp_post.text[:300]}")

        # After login, get a new _token for absen (from dashboard page)
        dashboard_url = f"{self._base_url}/dashboard"
        resp_dashboard = self._session.get(dashboard_url)
        if resp_dashboard.status_code != 200:
            raise Exception(f"Failed to load dashboard page after login: {resp_dashboard.status_code}")

        soup_dash = BeautifulSoup(resp_dashboard.text, "html.parser")
        token_input_dash = soup_dash.find("input", {"name": "_token"})
        if not token_input_dash or not token_input_dash.get("value"):
            raise Exception("Could not find _token input field on the dashboard page.")

        self._token = token_input_dash["value"]

    @staticmethod
    def _data_uri_to_bytes(data_uri: str) -> tuple[str, bytes]:
        """
        Convert data URI (data:image/png;base64,...) to (mime_type, bytes).
        """
        match = re.match(r"data:(?P<mime>[^;]+);base64,(?P<data>.+)$", data_uri)
        if not match:
            raise ValueError("Invalid data URI format")

        mime_type = match.group("mime")
        data_b64 = match.group("data")
        return mime_type, base64.b64decode(data_b64)

    def submit_presensi(
        self,
        image_data_uri: str,
        status: str,
        lokasi: str,
        lokasi_cabang: str,
        kode_jam_kerja: str = "JK03",
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """
        Send presence data. Returns parsed JSON response.
        Make sure to login() first!
        lokasi is set to a random point 2-6 m from lokasi_cabang when lokasi_cabang is "lat,lon".
        """
        import random
        import math

        def randomize_location(lat: float, lon: float, min_radius_m: float, max_radius_m: float) -> str:
            # Earth radius in meters
            R = 6378137
            distance = random.uniform(min_radius_m, max_radius_m)
            angle = random.uniform(0, 2 * math.pi)
            d_lat = distance * math.cos(angle) / R
            d_lon = distance * math.sin(angle) / (R * math.cos(math.radians(lat)))
            new_lat = lat + math.degrees(d_lat)
            new_lon = lon + math.degrees(d_lon)
            return f"{new_lat:.6f},{new_lon:.6f}"

        # If lokasi_cabang is "lat,lon", set lokasi to random point 2-6 m from it (each absen/schedule)
        parts = lokasi_cabang.strip().split(",")
        if len(parts) == 2:
            try:
                base_lat, base_lon = float(parts[0].strip()), float(parts[1].strip())
                lokasi = randomize_location(base_lat, base_lon, 2, 6)
            except ValueError:
                pass  # keep original lokasi if parse fails
        if not self._token:
            raise Exception("Not logged in or _token not set. Call login() first.")

        mime_type, image_bytes = self._data_uri_to_bytes(image_data_uri)
        # Server expects status as "1" (masuk/in) or "2" (keluar/out), same as browser form
        status_value = "1" if (str(status).strip().lower() == "in") else "2"

        # Multipart form: image as file (name=image, filename=image.png), rest as form fields
        files = {
            "image": ("image.png", image_bytes, mime_type or "image/jpeg"),
        }
        data = {
            "_token": self._token,
            "status": status_value,
            "lokasi": lokasi,
            "lokasi_cabang": lokasi_cabang,
            "kode_jam_kerja": kode_jam_kerja,
        }

        url = f"{self._base_url}/presensi"
        resp = self._session.post(
            url,
            data=data,
            files=files,
            timeout=timeout,
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()  # raise if HTTP error

        try:
            payload = resp.json()
        except ValueError:
            raise RuntimeError(f"Non-JSON response from presensi endpoint: {resp.text[:500]}")

        return payload


# Example usage flow:
if __name__ == "__main__":
    # Replace these values with your actual credentials and absen data
    user_id = "260200098"
    password = "260200098"
    status = "1"
    # lokasi is ignored when lokasi_cabang is "lat,lon" – then set to random 2–6 m from cabang
    lokasi = ""
    lokasi_cabang = "-7.316514,112.724501"
    kode_jam_kerja = "JK04"
    # You need a real data:image/png;base64,... string for actual absen
    fake_image_data_uri = "data:image/png;base64," + base64.b64encode(b"dummydata").decode()

    client = PresensiClient(user_id, password)
    print("Logging in...")
    client.login()
    print("Login successful. Now performing absen...")
    result = client.submit_presensi(
        image_data_uri=fake_image_data_uri,
        status=status,
        lokasi=lokasi,
        lokasi_cabang=lokasi_cabang,
        kode_jam_kerja=kode_jam_kerja
    )
    print("Absen Result:", result)