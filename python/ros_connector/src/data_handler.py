import csv
import re
from math import pow, sqrt
from os.path import dirname, join


class DataHandler(object):
    def __init__(self, data_file=None, log_queue=None):
        """ Constructor. Reads the data file into a multidimensional list.
            param: data_file [String]
            return: self [DataHandler]
        """
        self.log_queue = log_queue
        self.data_dir = dirname(data_file)
        # Read the given CSV file
        with open(data_file, newline='') as csvfile:
            raw_data = list(csv.reader(csvfile, delimiter=";"))

        # Pop the header to use as a reference for the fields in the data base
        self.header = raw_data.pop(0)
        self.header.append("#Shape")

        # Iterate through the raw data and insert it to the data table
        self.data = []
        nam_idx = self.header.index("#Name")
        self.x_idx = [head.lower() for head in self.header].index("x")
        self.y_idx = [head.lower() for head in self.header].index("y")
        self.id_idx = [head.lower() for head in self.header].index("id")
        for i, data_row in enumerate(raw_data):
            data_row[self.id_idx] = str(i)
            data_row.append(self._get_shape(data_row[nam_idx]))
            self.data.append([cell.lower() for cell in data_row])

        # Check which fields are searchable, they are indicated with a #-sign in the header.
        self.searchable_fields_idx = [i for i, field in enumerate(self.header) if
                                      field.startswith("#")]
        self.current_filter = []
        self.current_attributes = []
        self.reset_filter()

    def reset_filter(self):
        """ Reset the current filter to start over.
            param: N/A
            return: None
        """
        self.current_filter = []
        self.current_attributes = []

    def _get_shape(self, name):
        """ Return the shape description according to the name in the data.
            param: name [String]
            return: [String]
        """
        regex = r"^Brick \d+[X]\d+"
        if "Roof Tile" in name:
            return "slope"
        elif re.match(regex, name, re.M|re.I):
            return "regular"
        return "round"

    def _get_col(self, data, col_idx):
        """ Removes the column indicated by the col_index
            param: col_idx [int]
                    data [list of lists]
            return: [list]
        """
        return [row[col_idx] for row in data]

    def _get_attributes(self, data="all", field_idx="all"):
        """ Get the avaiable attributes from the fields indicated in the parameter.
            param:  field_idx [int, list or String]
                    data [list of lists or String]
            return: attributes [list]
        """
        if data == "all":
            data = self.data
        if field_idx == "all":
            field_idx = self.searchable_fields_idx
        elif isinstance(field_idx, int):
            field_idx = [field_idx]
        attributes = []
        for idx in field_idx:
            attributes += self._get_col(data, idx)
        return list(set(attributes))

    def filter(self, attributes):
        """ Creates a new filtered selection of the data according to new attributes.
            param: attributes [list]
            return: None
        """
        # Remove irrelevant attributes, i.e. those that doesn't occur in the data.
        relevant_attributes = self._get_attributes()
        self.current_attributes += [attribute for attribute in attributes if attribute in
                                    relevant_attributes]
        self.current_filter = [data_row for data_row in self.data if\
                               self._score(data_row) >= len(self.current_attributes)]
        return self.current_filter

    def _score(self, data_row):
        """ Meassure if the data_row maches the current filter.
            param: data_row [list]
            return: score [float]
        """
        data_attributes = self._get_attributes(data=[data_row])
        score = 0
        for data_attribute in data_attributes:
            for filter_attribute in self.current_attributes:
                if filter_attribute in data_attribute:
                    score += 1
                    break
        return score

    def update(self, update_dict):
        """ Find the item in the data base that is closest to the one as given in update_dict and
            update it.
            param: update_dict [dictionary]
            return: None
        """
        min_dist = 1000
        update_idx = None
        x_col = self._get_col(self.data, self.x_idx)
        y_col = self._get_col(self.data, self.y_idx)
        for i, (x_pos, y_pos) in enumerate(zip(x_col, y_col)):
            dist = self._euclidian(update_dict["x"], update_dict["y"], x_pos, y_pos)
            if dist < min_dist:
                min_dist = dist
                update_idx = i
        if update_idx and min_dist <= 0.02:
            self.data[update_idx][self.x_idx] = update_dict["x"]
            self.data[update_idx][self.y_idx] = update_dict["y"]
        else:
            self.log("Min closest block was {:.02f}cm away, no update".format(min_dist*100))

    def log(self, message):
        """ Send the message to the log queue
            params: message [String]
            return: None
        """
        if self.log_queue:
            self.log_queue.put("Data Handler#{}".format(message))

    def _euclidian(self, x1, y1, x2, y2):
        """ Calculate the euclidian distance in 2D-space.
            param: x1, y1, x2, y2 [Strings, points in the space]
            return [float]
        """
        return sqrt(pow(float(x1)-float(x2), 2)+pow(float(y1)-float(y2), 2))

    def remove(self, current_block):
        """ NOT IMPLEMENTED
        """
        pass

    def get_next_block(self):
        """ Pops the next block as a dictionary
            param: N/A
            return: block [dictionary] 
        """
        block = self.current_filter.pop(0)
        return {"id":block[self.id_idx], "x":block[self.x_idx], "y":block[self.y_idx]}

    def get_all_considered(self):
        """ Return all blocks considered as a list of dictionaries
            param: N/A
            return: blocks [list of dictionaries]
        """
        blocks = []
        for block in self.current_filter:
            blocks.append({"id":block[self.id_idx], "x":block[self.x_idx], "y":block[self.y_idx]})
        return blocks