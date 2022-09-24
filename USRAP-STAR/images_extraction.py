import requests

def extract_images(
    image_data,
    api_key,
    fov=90,
    pitch=0,
    size="640x640"
):
    """
    Find Google Street View images from the set of points returned from either
    an extract intersections method or an interpolate roads method.

    Parameters
    -------
    image_data : dict
        the input points. this method requires for there to be 'location' and 'heading'
        in the dictionary for it to work
    api_key : string
        the key that allows for the interaction with the Google API
    fov : int or float
        field of view
    pitch : int or float
        the vertical angle of the image
    size : string
        size of the image in the format of length x width in the format of a string
    """
    meta_base = 'https://maps.googleapis.com/maps/api/streetview/metadata?'
    pic_base = 'https://maps.googleapis.com/maps/api/streetview?'
    for images in image_data:
        if images.get('location') and images.get('heading'):
            meta_params = {'key': api_key, 'location': image_data['location']}
            pic_params = {'key': api_key,
                          'location':  images['location'],
                          'heading': images['heading'],
                          'fov': fov,
	                      'pitch': pitch,
                          'size': size}
        else:
            continue
    return

def find_image_metadata(
    image_data,
    api_key,
):
    return