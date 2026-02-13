import os
from kivy.app import App

def open_android_file_picker(callback):
    from jnius import autoclass
    from android import mActivity, activity

    Intent = autoclass('android.content.Intent')

    intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
    intent.addCategory(Intent.CATEGORY_OPENABLE)
    intent.setType("*/*")
    intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

    REQUEST_CODE = 1001

    def on_activity_result(request_code, result_code, data):
        if request_code != REQUEST_CODE:
            return

        activity.unbind(on_activity_result=on_activity_result)

        if data is None:
            callback(None)
            return

        uri = data.getData()
        callback(uri.toString() if uri else None)

    activity.bind(on_activity_result=on_activity_result)
    mActivity.startActivityForResult(intent, REQUEST_CODE)

def resolve_content_uri(uri):
    from jnius import autoclass
    from android import mActivity

    Uri = autoclass('android.net.Uri')
    parsed = Uri.parse(uri)

    resolver = mActivity.getContentResolver()
    stream = resolver.openInputStream(parsed)

    app_dir = App.get_running_app().user_data_dir
    path = os.path.join(app_dir, "book.fb2")

    with open(path, 'wb') as f:
        buf = bytearray(8192)
        while True:
            r = stream.read(buf)
            if r == -1:
                break
            f.write(buf[:r])

    stream.close()
    return path