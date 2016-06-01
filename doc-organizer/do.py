import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk



class MainWindow(Gtk.Window):
    def __init__(self):
        # Are we currently editing a name
        self.edit = False
        self.treeiter = None

        Gtk.Window.__init__(self, title="PDF Organizer")
        self.connect("key-press-event", self.handle_keypress)

        self.path = Gtk.TreePath.new_from_indices([0])

        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(main_vbox)

        content_hbox = Gtk.Box()
        main_vbox.pack_start(content_hbox, True, True, 0)

        self.name_entry = Gtk.Entry()
        main_vbox.pack_start(self.name_entry, True, True, 0)

        # Create a store and the tree view
        store = Gtk.ListStore(str)
        for i in range(10):
            store.append(["page %d" % i])
        self.store = store
        self.tree = self._create_tree_view(store)
        content_hbox.pack_start(self.tree, True, True, 0)

        # Create the image view
        self.imageview = Gtk.Image()
        content_hbox.pack_start(self.imageview, True, True, 0)

        self.grab_focus()
        self.select_first()

    def _create_tree_view(self, store):
        tree = Gtk.TreeView(store)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Document", renderer, text=0)
        tree.append_column(column)
        #tree.set_can_focus(False)
        tree.set_enable_search(False)
        return tree

    def handle_keypress(self, _, event):
        if not self.edit:
            if event.keyval == 106:
                self.select_next()
                return True
            if event.keyval == 107:
                self.select_prev()
                return True
            # Key 'e'
            if event.keyval == 101:
                self.edit_current()
                return True
        else:
            # Key Enter
            if event.keyval == 65293:
                self.end_edit_current()
                return True

        print(event.keyval)
        return False

    def select_first(self):
        self.tree.set_cursor(self.path, None, False)

    def select_next(self):
        self.path.next()
        self.tree.set_cursor(self.path, None, False)

    def select_prev(self):
        self.path.prev()
        self.tree.set_cursor(self.path, None, False)

    def edit_current(self):
        self.edit = True
        selection = self.tree.get_selection()
        model, iter = selection.get_selected()
        if iter != None:
            self.treeiter = iter
            self.name_entry.set_text(model[iter][0])
            self.name_entry.grab_focus()

    def end_edit_current(self):
        # Change the value on the list
        name = self.name_entry.get_text()
        if self.treeiter is not None:
            self.store.set_value(self.treeiter, 0, name)

        # Clean
        self.edit = False
        self.treeiter = None
        self.name_entry.set_text("")
        self.select_next()
        self.grab_focus()



def run_mainwindow():
    win = MainWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    run_mainwindow()
