import numpy
import qrcode, io, base64

INS = numpy.array([1,0,0,0])    
ADM = numpy.array([0,1,0,0])    
DIR = numpy.array([0,0,1,0])    
TRA = numpy.array([0,0,0,1])    

def userprofile2bit(user):
    """ Bit wise (1111) as institution administrator diractor trainer
        example:
            1000 is institution user
            0100 is administrator user
            0010 is diractor user
            0001 is trainer trainer
            
            1001 is institution and trainer user
            and so on...
    """
    u_ist       = int(user.profile.institution)
    u_adm       = int(user.profile.administrator)
    u_dir       = int(user.profile.director)
    u_tra       = int(user.profile.trainer)
    # print("helper.userprofile2bit", numpy.array([u_ist, u_adm, u_dir, u_tra]))
    
    return numpy.array([u_ist, u_adm, u_dir, u_tra])

def protocol_perm(user, x):
    # print("protocol_perm user", userprofile2bit(user))
    # print("protocol_perm x", x)
    u = userprofile2bit(user)
    y = u & x
    # print("protocol_perm y", y)
    return numpy.array_equal(y, x)

def qrcode_str2base64(string, version=None, error_correction=qrcode.constants.ERROR_CORRECT_Q, box_size=100, border=4):
    """
    https://pypi.org/project/qrcode/
    error_correction:
        ERROR_CORRECT_L About 7% or less errors can be corrected.
        ERROR_CORRECT_M About 15% or less errors can be corrected.
        ERROR_CORRECT_Q About 25% or less errors can be corrected.
        ERROR_CORRECT_H About 30% or less errors can be corrected.
    
    version:
        The version parameter is an integer from 1 to 40 that controls the size of the QR Code
        (the smallest, version 1, is a 21x21 matrix). Set to None and use the fit parameter when
        making the code to determine this automatically.
    
    box_size:    
    The box_size parameter controls how many pixels each “box” of the QR code is.
    
    border:
    The border parameter controls how many boxes thick the border should be
    (the default is 4, which is the minimum according to the specs).
    """
    qr = qrcode.QRCode(
                version=version,
                error_correction=error_correction,
                box_size=box_size,
                border=border
            )
    qr.add_data(string)
    qr.make(fit=True)
 
    # creates qrcode base64
    out = io.BytesIO()
    qr_img = qr.make_image()
    qr_img.save(out, 'PNG')
    return 'data: image/gif;base64, '+base64.b64encode(out.getvalue()).decode('utf-8')