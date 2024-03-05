import sys
import csv
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHeaderView, QLineEdit, QTableView, QComboBox, QProgressDialog, QLabel, QCheckBox, QPushButton, QHBoxLayout 
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QRegExp

def load_csv_data(file_name):
    data = []
    with open(file_name, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        data.append(headers)
        
        for row in reader:
            data.append(row)

    return data

def rearrange_data_columns(data):
    
    score_factor_index = data[0].index("Score Factor")
    
    for row in data:
        score_factor = row.pop(score_factor_index)
        row.insert(0, score_factor)
    
    return data

class CumulativeFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, headers, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = headers
        self.filters = {}
        self.text_filter = None
        self.player_count_filter = None
        self.min_year = None  # Initialize min_year
        self.max_year = None  # Initialize max_year
        self.min_avg_rating = None
        self.max_avg_rating = None
        self.min_weight = None
        self.max_weight = None

    def set_filter(self, column, filter_value):
        if filter_value:
            self.filters[column] = filter_value
        elif column in self.filters:
            del self.filters[column]
        self.invalidateFilter()
        
    def set_text_filter(self, column, text):
        self.text_filter = (column, text)
        self.invalidateFilter()
        
    def set_player_count_filter(self, column, player_count_filter):
        self.player_count_filter = (column, player_count_filter)
        self.invalidateFilter()
        
    def set_year_filter(self, min_year, max_year):
        self.min_year = min_year
        self.max_year = max_year
        self.invalidateFilter()
        
    def set_avg_rating_filter(self, min_avg_rating, max_avg_rating):
        self.min_avg_rating = min_avg_rating
        self.max_avg_rating = max_avg_rating
        self.invalidateFilter()

    def set_weight_filter(self, min_weight, max_weight):
        self.min_weight = min_weight
        self.max_weight = max_weight
        self.invalidateFilter()
    
    def filterAcceptsRow(self, source_row, source_parent):
           
        for column, filter_value in self.filters.items():
            index = self.sourceModel().index(source_row, column, source_parent)
            data = self.sourceModel().data(index)

            # Compare the data and filter value as strings
            data_str = str(data)
            filter_value_str = str(filter_value)

            if data_str != filter_value_str:
                return False

        if self.text_filter:
            column, text = self.text_filter
            index = self.sourceModel().index(source_row, column, source_parent)
            data = self.sourceModel().data(index)

            # Convert the data back to text if it's a number
            if isinstance(data, (int, float)):
                data = str(data)

            if str(text).lower() not in str(data).lower():
                return False

        if self.player_count_filter is not None:
            column, filter_count = self.player_count_filter
            index = self.sourceModel().index(source_row, column, source_parent)
            player_count = int(self.sourceModel().data(index))     
            
            if filter_count is None:
                pass
            elif filter_count == 8:
                if player_count < 8:
                    return False
            else:
                if player_count != int(filter_count):
                    return False              
                    
        # Year filter logic
        if self.min_year is not None or self.max_year is not None:
            year_index = self.sourceModel().index(source_row, self.headers.index("Year"), source_parent)
            year = int(self.sourceModel().data(year_index))

            if self.min_year is not None and year < self.min_year:
                return False
            if self.max_year is not None and year > self.max_year:
                return False
         
        # Average Rating filter logic
        if self.min_avg_rating is not None or self.max_avg_rating is not None:
            avg_rating_index = self.sourceModel().index(source_row, self.headers.index("Average Rating"), source_parent)
            avg_rating = float(self.sourceModel().data(avg_rating_index))

            if (self.min_avg_rating is not None and avg_rating < self.min_avg_rating) or \
               (self.max_avg_rating is not None and avg_rating > self.max_avg_rating):
                return False

        # Weight filter logic
        if self.min_weight is not None or self.max_weight is not None:
            weight_index = self.sourceModel().index(source_row, self.headers.index("Weight"), source_parent)
            weight = float(self.sourceModel().data(weight_index))

            if (self.min_weight is not None and weight < self.min_weight) or \
               (self.max_weight is not None and weight > self.max_weight):
                return False         

        return True

class MainWindow(QMainWindow):
    def __init__(self, data):
        super().__init__()

        self.data = data
        
        self.setWindowTitle("Game Data")
        
        # Create the table view and its model
        self.table_view = QTableView()
        self.model = QStandardItemModel()
        self.table_view.setModel(self.model)
        self.setCentralWidget(self.table_view)

        # Set up the table view
        self.setup_table(data)
        self.bold_headers()
        
        # Create a QSortFilterProxyModel for filtering
        self.proxy_model = CumulativeFilterProxyModel(self.data[0], parent=self.table_view)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.table_view.setModel(self.proxy_model)

        # Create and show the filter window
        self.filter_window = FilterWindow(self)
        self.filter_window.show()

        # Resize the main window to fit the table columns
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.resize(self.table_view.horizontalHeader().length()+100, 1200)
        
        self.sort_by_score_factor()  # Add this line to sort by Score Factor on load
        
    def closeEvent(self, event):
        self.filter_window.close()
        event.accept()    

    def bold_headers(self):
        header_font = self.table_view.horizontalHeader().font()
        header_font.setBold(True)
        self.table_view.horizontalHeader().setFont(header_font)

    def setup_table(self, data):
        # Set the row and column count
        self.model.setRowCount(len(data) - 1)
        self.model.setColumnCount(len(data[0]))
        
        # Set the horizontal headers        
        headers = ["Score\nFactor", "Game ID", "Game Title", "Type", "Year", "Average\nRating", "Number\nof\n Voters", "Weight", "Weight\nVotes", "Owned", "Player\nCount", "Best\n%", "Best\nVotes", "Rec.\n%", "Rec.\nVotes", "Not\n%", "Not\nVotes", "Total\nVotes", "Player\nCount\nScore\n(unadjusted)", "Player\nCount\nScore", "Playable"]
        
        self.model.setHorizontalHeaderLabels(headers)

        # Hide the vertical header
        self.table_view.verticalHeader().hide()

        # Create the progress dialog
        progress_dialog = QProgressDialog("Loading data...", "Cancel", 0, len(data) - 1, self)
        progress_dialog.setWindowTitle("Loading Data")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(0)
        progress_dialog.setMinimumWidth(500)  # Set the minimum width of the progress dialog

        # Populate the table view
        for row in range(1, len(data)):
            for col in range(len(data[row])):
                item = QStandardItem(str(data[row][col]))

                # Check if the value in the first row is numeric
                try:
                    float(data[1][col])  # Check if the value can be cast to a float
                    is_numeric = True
                except ValueError:
                    is_numeric = False

                # If the value is numeric, set the data type to a number
                if is_numeric:
                    try:
                        number = float(data[row][col])
                    except ValueError:
                        number = int(data[row][col])
                    item.setData(number, Qt.DisplayRole)

                self.model.setItem(row - 1, col, item)

            # Update the progress dialog
            progress_dialog.setValue(row)
            progress_dialog.setLabelText(f"Loading data... ({row}/{len(data) - 1})")  # Update the label text with progress
            QApplication.processEvents()
            if progress_dialog.wasCanceled():
                break

        # Set the table view properties
        self.table_view.setSortingEnabled(True)
        
        header_row = self.data[0]
        player_count_score_unadjusted_index = header_row.index("Player Count Score (unadjusted)")

        # Hide the "Player Count Score (unadjusted)" column
        header = self.table_view.horizontalHeader()
        header.hideSection(player_count_score_unadjusted_index)



    def filter_game_title(self, text):
        self.proxy_model.set_text_filter(self.data[0].index("Game Title"), text)

    def filter_playable(self, text):
        if text == "All":
            self.proxy_model.set_filter(self.data[0].index("Playable"), None) 
        else:
            self.proxy_model.set_filter(self.data[0].index("Playable"), text)
            
        self.sort_by_score_factor()
         
    def filter_owned(self, text):
        if text == "All":
            self.proxy_model.set_filter(self.data[0].index("Owned"), None)  
        else:
            self.proxy_model.set_filter(self.data[0].index("Owned"), text)
            
        self.sort_by_score_factor()
        
    def filter_type(self, text):
        if text == "All":
            self.proxy_model.set_filter(self.data[0].index("Type"), None) 
        else:
            self.proxy_model.set_filter(self.data[0].index("Type"), text)
            
        self.sort_by_score_factor()     
        
    def filter_player_count(self, text):
        if text == "All":
            self.proxy_model.set_player_count_filter(self.data[0].index("Player Count"), None)
        elif text == "8+":
            self.proxy_model.set_player_count_filter(self.data[0].index("Player Count"), 8)
        else:
            player_count = int(text)
            self.proxy_model.set_player_count_filter(self.data[0].index("Player Count"), player_count)
            
        self.sort_by_score_factor()

        
    def sort_by_score_factor(self):
        header = self.table_view.horizontalHeader()
        score_factor_index = header.logicalIndex(header.count() - 1)  # Default to the last column in case the header is not found
        
        for i in range(header.count()):
            if header.model().headerData(i, Qt.Horizontal) == "Score\nFactor":
                score_factor_index = i
                break

        self.table_view.sortByColumn(score_factor_index, Qt.DescendingOrder)

class FilterWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window        
        self.setWindowTitle("Filters")
        
        # Set the font size
        font = self.font()
        font.setPointSize(12)
        self.setFont(font)

        # Create the main layout
        layout = QVBoxLayout(self)

        # Game Title filter
        layout.addWidget(QLabel("Game Title:"))
        self.game_title_filter = QLineEdit()
        self.game_title_filter.textChanged.connect(self.main_window.filter_game_title)
        layout.addWidget(self.game_title_filter)

        # Owned filter
        layout.addWidget(QLabel("\nOwned:"))
        self.owned_filter = QComboBox()
        self.owned_filter.addItem("All")
        self.owned_filter.addItem("Owned")
        self.owned_filter.addItem("Not Owned")
        self.owned_filter.currentTextChanged.connect(self.main_window.filter_owned)
        layout.addWidget(self.owned_filter)

        # Type filter
        layout.addWidget(QLabel("\nType:"))
        self.type_filter = QComboBox()
        self.type_filter.addItem("All")
        self.type_filter.addItem("Base Game")
        self.type_filter.addItem("Expansion")
        self.type_filter.currentTextChanged.connect(self.main_window.filter_type)
        layout.addWidget(self.type_filter)
        
        # Playable filter
        layout.addWidget(QLabel("\nPlayable:"))
        self.playable_filter = QComboBox()
        self.playable_filter.addItem("All")
        self.playable_filter.addItem("Playable")
        self.playable_filter.addItem("Not Playable")
        self.playable_filter.currentTextChanged.connect(self.main_window.filter_playable)
        self.playable_filter.setCurrentIndex(1)  # Add this line to select "Playable" by default
        layout.addWidget(self.playable_filter)
        
        # Player Count filter
        layout.addWidget(QLabel("\nPlayer Count:"))
        self.player_count_filter = QComboBox()
        self.player_count_filter.addItem("All")
        for i in range(1, 8):
            self.player_count_filter.addItem(str(i))
        self.player_count_filter.addItem("8+")
        self.player_count_filter.currentTextChanged.connect(self.main_window.filter_player_count)
        layout.addWidget(self.player_count_filter)

        # Year filter
        layout.addWidget(QLabel("\nYear:"))
        self.min_year_filter = QLineEdit()
        self.min_year_filter.setPlaceholderText("Min Year")
        self.max_year_filter = QLineEdit()
        self.max_year_filter.setPlaceholderText("Max Year")
        self.year_filter_button = QPushButton("Set Year Filter")
        self.year_filter_button.clicked.connect(self.set_year_filter)

        year_filter_layout = QHBoxLayout()
        year_filter_layout.addWidget(self.min_year_filter)
        year_filter_layout.addWidget(self.max_year_filter)
        year_filter_layout.addWidget(self.year_filter_button)
        layout.addLayout(year_filter_layout)
        
        # Average Rating filter
        layout.addWidget(QLabel("\nAverage Rating:"))
        self.min_avg_rating_filter = QLineEdit()
        self.min_avg_rating_filter.setPlaceholderText("Min Avg Rating")
        self.max_avg_rating_filter = QLineEdit()
        self.max_avg_rating_filter.setPlaceholderText("Max Avg Rating")
        self.avg_rating_filter_button = QPushButton("Set Avg Rating Filter")
        self.avg_rating_filter_button.clicked.connect(self.set_avg_rating_filter)

        avg_rating_filter_layout = QHBoxLayout()
        avg_rating_filter_layout.addWidget(self.min_avg_rating_filter)
        avg_rating_filter_layout.addWidget(self.max_avg_rating_filter)
        avg_rating_filter_layout.addWidget(self.avg_rating_filter_button)
        layout.addLayout(avg_rating_filter_layout)

        # Weight filter
        layout.addWidget(QLabel("\nWeight:"))
        self.min_weight_filter = QLineEdit()
        self.min_weight_filter.setPlaceholderText("Min Weight")
        self.max_weight_filter = QLineEdit()
        self.max_weight_filter.setPlaceholderText("Max Weight")
        self.weight_filter_button = QPushButton("Set Weight Filter")
        self.weight_filter_button.clicked.connect(self.set_weight_filter)

        weight_filter_layout = QHBoxLayout()
        weight_filter_layout.addWidget(self.min_weight_filter)
        weight_filter_layout.addWidget(self.max_weight_filter)
        weight_filter_layout.addWidget(self.weight_filter_button)
        layout.addLayout(weight_filter_layout)

        # Set the layout to the filter window and set its size
        layout.setContentsMargins(50, 50, 50, 50)
        self.setLayout(layout)
        self.setMinimumSize(400, 300)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
    def set_year_filter(self):
        min_year = int(self.min_year_filter.text()) if self.min_year_filter.text() else None
        max_year = int(self.max_year_filter.text()) if self.max_year_filter.text() else None
        self.main_window.proxy_model.set_year_filter(min_year, max_year)
        
    def set_avg_rating_filter(self):
        min_avg_rating = float(self.min_avg_rating_filter.text()) if self.min_avg_rating_filter.text() else None
        max_avg_rating = float(self.max_avg_rating_filter.text()) if self.max_avg_rating_filter.text() else None
        self.main_window.proxy_model.set_avg_rating_filter(min_avg_rating, max_avg_rating)

    def set_weight_filter(self):
        min_weight = float(self.min_weight_filter.text()) if self.min_weight_filter.text() else None
        max_weight = float(self.max_weight_filter.text()) if self.max_weight_filter.text() else None
        self.main_window.proxy_model.set_weight_filter(min_weight, max_weight)

    def closeEvent(self, event):
        self.main_window.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    data = load_csv_data('PlayerCountDataList.csv')
    data = rearrange_data_columns(data)     
    
    main_window = MainWindow(data)
    main_window.show()

    sys.exit(app.exec_())

