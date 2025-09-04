# recent_items_list

A list -like class which can "bump" items to the top.

By default, only the last 10 items are kept in the list. If a new item is
"bumped" to the beginning of a RecentItemsList that already has 10 items, the
item at the end of the list is dropped. You can change this by setting the
"maxlen" property on an instance of RecentItemsList.

The two most used methods are "bump(<item>)" and "remove(<item>)".

### When an item needs to be added OR moved to the top:

	self._recent_files.bump(filename)

### When item needs to be removed:

	self._recent_files.remove(filename)

## Example:

This is a simple implementation of a "Recent Files" menu.

### Initializing

	def __init__(self):
		self._recent_files = RecentItemsList(self.settings.value("recent_files", defaultValue = []))
		self.menuOpen_Recent.aboutToShow.connect(self.fill_recent_files)

### Filling the menu:

	@pyqtSlot()
	def fill_recent_files(self):
		self.menuOpen_Recent.clear()
		actions = []
		for filename in self._recent_files:
			action = QAction(filename, self)
			action.triggered.connect(partial(self.load_file, filename))
			actions.append(action)
		self.menuOpen_Recent.addActions(actions)

### Saving to QSettings:

	self.settings.setValue("recent_files", self._recent_files.items)

## Auto-save

Optionally, you provide a callback which will be called whenever the list changes:

	self._recent_files = RecentItemsList(self.settings.value("recent_files", defaultValue = []))
	self._recent_files.on_change(self.save_recent_files)

	def save_recent_files(self, items):
		self.settings.setValue("recent_files", items)

### Another implementation:

	def recent_files():
		global RECENT_FILES
		def sync(items):
			settings().setValue(KEY_RECENT_FILES, items)
		if RECENT_FILES is None:
			RECENT_FILES = RecentItemsList(settings().value(KEY_RECENT_FILES, []))
			RECENT_FILES.on_change(sync)
		return RECENT_FILES

