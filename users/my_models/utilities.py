import os, io
import datetime
from PIL import Image

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.files.uploadedfile import InMemoryUploadedFile


# ###### CLASSES #########
class Validators(object):
    @staticmethod
    def validate_prevent_future_date(value):
        """
        Ensure that the age of the user is not younger than two years
        or in the future
        """
        now = datetime.date.today()

        if isinstance(value, str):
            value = datetime.date.fromisoformat(value)
        if value > now:
            raise ValidationError(_("Your birth date %(dob)s should not be in the future"),
                                  params={'dob': value})
        return value

    @staticmethod
    def validate_shepherding_structure(value, obj):
        """
        Ensure that the shepherd are not shepherd and sub shepherd of themself
        """

        username = obj.username

        if username == value:
            raise ValidationError(_("You can't be shepherd of yourself"))


    @staticmethod
    def validate_sub_shepherd_structure(value, obj):
        """
        Ensure that the subsherd are not shepherd of them
        """


# ###### FUNCTIONS  #################

def get_user_name(object, fname):
    _, ext = os.path.splitext(fname)
    username = object.username
    return f"profile_pics/{username}{ext}"


def convert_image_to_webp(image):
    # Open the image using Pillow
    pil_image = Image.open(image)

    # Create an im-memory stream to save the converted image
    webp_io = io.BytesIO()
    pil_image.save(webp_io, 'webp')

    # Create an InMemoryUploadedFile object with the converted image
    webp_file = InMemoryUploadedFile(webp_io, 'profile_pic',
                                     f"{image.name.split('.')[0]}.webp",
                                     'image/webp', webp_io.tell(), None
                                     )

    return webp_file


def convert_image_in_path_to_webp(path):
    images = os.listdir(path)

    for img in images:
        pass
