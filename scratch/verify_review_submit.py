import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:3000"

def test_static_files():
    print("Testing static files...")
    # Check style.css
    req = urllib.request.urlopen(f"{BASE_URL}/static/css/style.css")
    css = req.read().decode('utf-8')
    assert ".modal-backdrop.open" in css, "Missing .modal-backdrop.open in style.css"
    assert ".modal-backdrop.active" in css, "Missing .modal-backdrop.active in style.css"
    assert ".form-group.has-error .field-error" in css, "Missing has-error field-error in style.css"
    assert ".portal-toast" in css, "Missing portal-toast in style.css"
    print("[OK] style.css has all required modal, error, and toast CSS classes")

    # Check app.js
    req_js = urllib.request.urlopen(f"{BASE_URL}/static/js/app.js")
    js = req_js.read().decode('utf-8')
    assert "reviewModal.classList.add('active', 'open')" in js, "Missing active/open add in app.js"
    assert "showToast" in js, "Missing showToast in app.js"
    assert "validateAll" in js, "Missing validateAll in app.js"
    print("[OK] app.js has updated review modal activation and toast logic")

def test_submit_validation():
    print("\nTesting backend submission with missing fields...")
    data = urllib.parse.urlencode({
        "full_name": "",
        "registration_number": ""
    }).encode('utf-8')

    req = urllib.request.Request(f"{BASE_URL}/submit", data=data, headers={
        "X-Requested-With": "XMLHttpRequest"
    })

    try:
        urllib.request.urlopen(req)
        print("[FAIL] Expected 400 validation error, but got success")
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode('utf-8'))
        assert body["success"] is False
        assert len(body["errors"]) > 0
        print(f"[OK] Correctly rejected with validation errors: {len(body['errors'])} errors returned")

def test_submit_success():
    print("\nTesting successful submission...")
    data = urllib.parse.urlencode({
        "full_name": "Priya Dharshini",
        "registration_number": "422122104999",
        "email": "priya.d@example.com",
        "phone": "9876543219",
        "degree_department": "B.E Computer Science and Engineering",
        "institution_name": "MIT Chennai",
        "institution_location": "Chromepet, Chennai",
        "internship_domain": "Fullstack Development (python)",
        "start_date": "2026-10-01",
        "end_date": "2026-10-31",
        "format_type": "Offline"
    }).encode('utf-8')

    req = urllib.request.Request(f"{BASE_URL}/submit", data=data, headers={
        "X-Requested-With": "XMLHttpRequest"
    })

    resp = urllib.request.urlopen(req)
    body = json.loads(resp.read().decode('utf-8'))
    print(f"Response: {body}")
    assert body["success"] is True
    assert "redirect_url" in body
    print(f"[OK] Successfully submitted. Application ID: {body.get('application_id')}, Redirect: {body.get('redirect_url')}")

    # Verify success page loads
    succ_req = urllib.request.urlopen(f"{BASE_URL}{body['redirect_url']}")
    assert succ_req.status == 200
    print("[OK] Success page loaded with status 200")

if __name__ == "__main__":
    test_static_files()
    test_submit_validation()
    test_submit_success()
    print("\nALL SYSTEM TESTS PASSED SUCCESSFULLY!")
