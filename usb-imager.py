import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import pyudev
import os

context = pyudev.Context()

def get_size(device: pyudev.Device):
    stat = os.statvfs(device.device_node)
    bytes = stat.f_blocks * stat.f_frsize
    return round(bytes / (10 ** 9))

def get_usb_devices():
    devices = []
    for device in context.list_devices(subsystem='block', DEVTYPE='disk'):
            # Only add usb devices
            if device.get('ID_BUS') == "usb":
                devices.append(device)
    return devices

class Window(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="USB Imager", resizable=False)
        self.resizable = False
        self.__create_window()
        self.button_refresh_drives.connect("clicked", self.update_combobox)
        self.button_choose_file.connect("clicked", self.choose_file)
        self.button_start.connect("clicked", self.on_write)

    def __create_window(self):
        spacing = 20
        margin = 10

        self.hboxes = []

        self.hboxes.append(Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=spacing, margin=margin))
        self.hboxes[0].pack_start(Gtk.Label(label="Image/ISO"), False, False, 0)
        self.file_name = Gtk.Entry(width_chars=50)
        self.hboxes[0].pack_start(self.file_name, True, True, 0)
        self.button_choose_file = Gtk.Button(label="Choose file")
        self.hboxes[0].pack_end(self.button_choose_file, False, False, 0)

        self.hboxes.append(Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=spacing, margin=margin))
        
        self.combobox_drive = self.generate_drives_combobox()
        self.hboxes[1].pack_start(Gtk.Label(label="USB Drive"), False, False, 0)
        self.hboxes[1].pack_start(self.combobox_drive, True, True, 0)
        self.button_refresh_drives = Gtk.Button(label="Refresh")
        self.hboxes[1].pack_end(self.button_refresh_drives, False, False, 0)

        self.hboxes.append(Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=spacing, margin=margin))
        self.button_start = Gtk.Button(label="Write")
        self.hboxes[2].pack_end(self.button_start, True, True, 0)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin=margin)
        for hbox in self.hboxes:
            self.vbox.pack_start(hbox, False, True, 0)
        self.add(self.vbox)

    def generate_drives_combobox(self):
        combobox_drives = Gtk.ComboBoxText()
        for device in get_usb_devices():
            path = device.device_node
            combobox_drives.append(path, "{0} ({1} {2} GB)".format(path, device.get('ID_MODEL'), get_size(device)))
        combobox_drives.set_entry_text_column(1)
        return combobox_drives

    def update_combobox(self, _):
        print("refresh")
        self.hboxes[1].remove(self.combobox_drive)
        self.combobox_drive = self.generate_drives_combobox()
        self.hboxes[1].pack_start(self.combobox_drive, True, True, 0)
        self.hboxes[1].reorder_child(self.combobox_drive, 1)
        self.combobox_drive.show_all()

    def choose_file(self, _):
        dialog = Gtk.FileChooserDialog(title="Select an image/ISO file")
        dialog.add_buttons("Select", Gtk.ResponseType.OK, "Cancel", Gtk.ResponseType.CLOSE)
        dialog.connect("response", self.on_select_file)
        response = dialog.run()
        
    def on_select_file(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            self.file_name.set_text(dialog.get_filename())
        dialog.destroy()
        print(response)
    
    def on_write(self, _):
        self.remove(self.vbox)
        progress = Gtk.ProgressBar()
        self.add(progress)
        self.show_all()

window = Window()
window.connect("destroy", Gtk.main_quit)
window.show_all()
Gtk.main()
