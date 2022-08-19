from PyQt5 import QtCore
# from PySide6.QtCore import Qt



class TableModel(QtCore.QAbstractTableModel):
    """Creating a Table Model for PyQt5 using the procedure:
    https://www.pythonguis.com/tutorials/pyqt6-qtableview-modelviews-numpy-pandas/

    Args:
        QtCore ([type]): [description]
    """    
    def __init__(self,data):
        """_summary_

        Args:
            data (pandas DataFrame, list): dataset to be displayed in a table
        """        
        super(TableModel,self).__init__()
        self._data = data

    def headerData(self, section, orientation, role):
        """_summary_

        Args:
            section (_type_): _description_
            orientation (_type_): _description_
            role (_type_): _description_

        Returns:
            _type_: _description_
        """        
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[section]
        return super().headerData(section, orientation, role)

    def data(self,index,role):
        """_summary_

        Args:
            index (_type_): _description_
            role (_type_): _description_

        Returns:
            _type_: _description_
        """        
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if isinstance(self._data, list):
                return self._data[index.row()][index.column()]
            value = self._data.iloc[index.row()][index.column()]
            return str(value)

    def rowCount(self, index):
        """_summary_

        Args:
            index (_type_): _description_

        Returns:
            _type_: _description_
        """        
        if isinstance(self._data, list):
            return len(self._data)
        return self._data.shape[0]

    def columnCount(self, index):
        """_summary_

        Args:
            index (_type_): _description_

        Returns:
            _type_: _description_
        """        
        if isinstance(self._data, list):
            return len(self._data[0])
        return self._data.shape[1]

    