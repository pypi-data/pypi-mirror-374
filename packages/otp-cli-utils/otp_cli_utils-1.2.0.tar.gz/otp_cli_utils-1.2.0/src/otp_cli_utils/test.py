from services import img_services, otp_services, qr_services
from utils import msg_utils


def main():
    secret = otp_services.generate_otp_secret()
    uri = otp_services.generate_uri(secret, "dilanka@gmail.com", "dilanka")
    img = qr_services.generate_qr_code(uri)
    msg = img_services.save_image(img, "test")
    msg_utils.print_success_msg(msg=msg)


if __name__ == "__main__":
    main()
