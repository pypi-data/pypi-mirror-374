import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline, PchipInterpolator, UnivariateSpline
from typing import Optional, Sequence



class DataManipulation:
    VERSION = 'Kantris.DataManipulation: 0.1.2'
    @staticmethod
    def LinearInterpol(x, xp, fp):
        """"
        x: target x-values
        xp: x-values of data
        fp: y-values of data
        """
        return np.interp(x, xp, fp)
    @staticmethod
    def CubicInterpol(x, xp, fp, bc_type='natural', extrapolate=True):
        if not np.all(np.diff(xp) > 0):
            # Sortiere xp und fp gemeinsam nach xp
            idx_sort = np.argsort(xp)
            xp = xp[idx_sort]
            fp = fp[idx_sort]


        cs = CubicSpline(xp, fp, bc_type=bc_type, extrapolate=extrapolate)
        return cs(x)
    @staticmethod
    def HermiteInterpol(x, xp, fp, extrapolate=True):
        pchip = PchipInterpolator(xp, fp, extrapolate=extrapolate)
        return pchip(x)
    @staticmethod
    def UnivariateInterpol(x, xp, fp, s):
        pchip = UnivariateSpline(xp, fp, s=s)
        return pchip(x)
    

class Array:
    """
    Methods:
        Col
    """
    VERSION = 'Kantris.Array: 0.1.1'


    @staticmethod
    def Merge(*arrays: np.ndarray) -> np.ndarray:
        """
        Nimmt beliebig viele NumPy-Arrays (1D oder 2D) und gibt ein 2D-Array zurück,
        in dem alle 1D-Eingaben als Spalten angeordnet sind. Falls ein Input 2D ist,
        werden seine Spalten jeweils als separate 1D-Arrays behandelt.

        Parameters
        ----------
        *arrays : np.ndarray
            Eine beliebige Anzahl von 1D- oder 2D-NumPy-Arrays.

        Returns
        -------
        np.ndarray
            Ein 2D-Array der Form (L, N), wobei L die gemeinsame Länge aller
            Spalten und N die Gesamtanzahl der resultierenden Spalten ist.

        Raises
        ------
        ValueError
            Wenn kein Array übergeben wird, ein Array weniger als 1D bzw. mehr als 2D ist
            oder die Längen der resultierenden Spalten nicht übereinstimmen.
        """
        if not arrays:
            raise ValueError("Mindestens ein Array muss übergeben werden.")

        cols = []
        for arr in arrays:
            arr = np.asarray(arr)
            if arr.ndim == 1:
                cols.append(arr)
            elif arr.ndim == 2:
                # Spalten einzeln hinzufügen
                for j in range(arr.shape[1]):
                    cols.append(arr[:, j])
            else:
                raise ValueError(
                    f"Eingabe mit ndim={arr.ndim} wird nicht unterstützt (nur 1D oder 2D).")
        
        # Prüfen, ob wirklich 1D-Spalten vorliegen und gleiche Länge haben
        lengths = [col.shape[0] for col in cols]
        if len(set(lengths)) != 1:
            raise ValueError(
                "Alle resultierenden Spalten müssen dieselbe Länge haben.")

        # Spaltenweises Zusammenfügen
        return np.column_stack(cols)

    
    @staticmethod
    def Col(array: np.ndarray, col: int) -> np.ndarray:
        return array[:, col]

    @staticmethod
    def Normalise(array, mode: str = "standard", col: int|tuple[int]|list[int] = 0) -> np.ndarray:
        """
        Normalisiert bestimmte Spalten eines Arrays nach verschiedenen Methoden.

        Args:
            array (np.ndarray): Eingabedaten.
            columns (list[str] | str): Liste der zu normalisierenden Spaltenindexe.
            Arg (str): Optionen:
                - "standard": (default) Mittelwert = 0, Std-Abw = 1
                - "mean": nur Mittelwertzentrierung
                - "start": Startwert auf 0 setzen
                - "amplitude": Skaliere Werte auf [0, 1]

        Returns:
            np.ndarray: Neues Array mit normalisierten Spalten.
        """
        if isinstance(col, (tuple, list)):
            for index in col:
                if not isinstance(index, int):
                    print(index, 'is invalid column index')
                    return array
                array = Array.Normalise(array, mode, index)
            return array
        
        elif isinstance(col, int):
            column = Array.Col(array, col)
            if mode in ('standard', 'standardise', 'std'):
                mean = column.mean()
                std = column.std()
                if std != 0:
                    column = (column - mean) / std

            elif mode in ('mean',):
                column = column - column.mean()
            
            elif mode in ('start',):
                column = column - column[0]
            
            elif mode in ('normal', 'normalise', 'norm'):
                min = column.min()
                max = column.max()
                column = column - min
                column = column/(max-min)

            else:
                print(mode, 'is invalid normalisation mode')
                return array
            
            array[:, col] = column
            return array
        
        else:
            print(col, 'is invalid column index')
            return array

    @staticmethod
    def Scale(array, scale: float, col: int|tuple[int]|list[int] = 0) -> np.ndarray:
        if isinstance(col, (tuple, list)):
            for index in col:
                if not isinstance(index, int):
                    print(index, 'is invalid column index')
                    return array
                array = Array.Scale(array, index)
            return array
        
        elif isinstance(col, int):
            array[:, col] = array[:, col]*scale
            return array
        else:
            print(col, 'is invalid column index')
            return array
    def RemoveOutliers(
        data: np.ndarray,
        threshold: float,
        cols: Optional[Sequence[int]] = None
    ) -> np.ndarray:
        """
        Entfernt alle Zeilen aus `data`, in denen in den angegebenen Spalten
        mindestens ein Wert mehr als `threshold` Standardabweichungen vom 
        jeweiligen Spaltenmittelwert abweicht.

        Parameters
        ----------
        data : np.ndarray
            2D-Array mit numerischen Werten, Form (n_samples, n_features).
        threshold : float
            Anzahl der Standardabweichungen, ab der ein Wert als Ausreißer gilt.
        cols : Sequence[int], optional
            Liste der Spalten-Indizes, die auf Ausreißer geprüft werden sollen.
            Standardmäßig (None) wird jede Spalte geprüft.

        Returns
        -------
        np.ndarray
            Gefiltertes 2D-Array mit allen "ausreißerfreien" Zeilen.
        """
        n_samples, n_features = data.shape

        # Falls keine Spalten angegeben, prüfen wir alle
        if cols is None:
            cols = np.arange(n_features)
        else:
            # in np-Array umwandeln, damit data[:, cols] funktioniert
            cols = np.array(cols, dtype=int)

        # Nur die zu prüfenden Spalten extrahieren
        sub = data[:, cols]

        # Mittelwert und Standardabweichung der Submatrix berechnen
        mean = np.mean(sub, axis=0)
        std  = np.std(sub,  axis=0)

        # Absolute Abweichung jeder Zeile in den gewählten Spalten vom Mittelwert
        deviation = np.abs(sub - mean)

        # Maske: True, wenn in ALLEN geprüften Spalten Abweichung ≤ threshold·std
        keep_mask = np.all(deviation <= threshold * std, axis=1)

        # Gefiltertes Array zurückgeben (inkl. unveränderter Spalten)
        return data[keep_mask]


class Dataframe:
    """
    Methods:
        ReadFromCSV
        ColumnToArray
        AddCol
        Normalise
    """
    VERSION = 'Kantris.Dataframe: 0.1.0'


    @staticmethod
    def Functions():
        text = """
        ReadFromCSV()
        ColumnToArray()
        AddCol()
        Normalise()
        """
        print(text)

    @staticmethod
    def ReadFromCSV(filepath: str, sep: str = ',') -> pd.DataFrame:
        """
        Liest eine CSV-Datei ein (erste Zeile als Header) und gibt ein pandas DataFrame zurück.

        Args:
            filepath (str): Pfad zur CSV-Datei.
            sep (str, default = ','): Seperator der Datei.

        Returns:
            pd.DataFrame: DataFrame mit den eingelesenen Daten.
        """
        return pd.read_csv(filepath, sep=sep)
    
    @staticmethod
    def ColumnToArray(df: pd.DataFrame, columns: list[str]) -> np.ndarray:
        """
        Liest die angegebenen Spalten aus dem DataFrame aus und gibt sie als NumPy-Array zurück.

        Args:
            df (pd.DataFrame): Das DataFrame, aus dem die Spalten entnommen werden sollen.
            columns (list[str]): Liste der Spaltennamen, die extrahiert werden sollen.

        Returns:
            np.ndarray: 2D-Array mit den Werten der ausgewählten Spalten (Form: (n_rows, len(columns))).
        """
        return df[columns].to_numpy()
    
    @staticmethod
    def AddCol(
        df: pd.DataFrame,
        column: np.ndarray,
        name: str = None,
        interpol: tuple = None
    ) -> pd.DataFrame:
        """
        Fügt dem DataFrame df eine neue Spalte hinzu mit ggf. Interpolation auf eine Spalte.

        Args:
            df (pd.DataFrame): Das Ziel-DataFrame, dem eine Spalte hinzugefügt wird.
            column (np.ndarray): 1D-Array mit den Werten, die als neue Spalte eingefügt werden sollen.
            name (str, optional): Name der neuen Spalte. 
                                  Wenn None, wird der nächste Index (als String) verwendet.
            interpol (tuple, optional): Tuple der Form
                (spaltenname: str, x_vals: np.ndarray, [method: str]).
                - spaltenname: Name der existierenden Spalte in df, deren Werte (y) als Stützwerte dienen.
                - x_vals: 1D-Array von x-Koordinaten, die zu df[spaltenname] gehören.
                - method (optional): 'linear' oder 'cubic' (Standard: 'linear').

                Wenn interpol angegeben ist, wird zunächst eine Interpolation 
                von df[spaltenname] an den Stützstellen x_vals auf die neuen x-Werte 
                column vorgenommen. Das Ergebnis dieser Interpolation wird 
                dann als neue Spalte eingesetzt.

        Returns:
            pd.DataFrame: Das DataFrame mit der hinzugefügten Spalte (inplace).
        """
        # 1. Überprüfen, dass column 1D ist
        column = np.asarray(column)
        if column.ndim != 1:
            raise ValueError("Array for Column must be of Dimension 1")

        # 2. Interpolations-Logik
        if interpol is not None:
            if not (isinstance(interpol, tuple) and 2 <= len(interpol) <= 3):
                raise ValueError(
                    "interpol muss ein Tuple sein: "
                    "(spaltenname: str, x_vals: np.ndarray, [method: str])"
                )
            spaltenname = interpol[0]
            x_vals = np.asarray(interpol[1])
            method = 'linear' if len(interpol) == 2 else interpol[2]

            # Spaltenname existiert?
            if spaltenname not in df.columns:
                raise KeyError(f"Spalte '{spaltenname}' nicht im DataFrame gefunden.")

            y_vals = df[spaltenname].to_numpy()
            if y_vals.ndim != 1:
                raise ValueError(f"Spalte '{spaltenname}' muss 1D sein.")

            # Überprüfen, dass x_vals 1D und gleich lang wie y_vals ist
            if x_vals.ndim != 1:
                raise ValueError(
                    "x_vals muss 1D sein."
                )

            # Interpolation durchführen
            if method == 'linear':
                new_vals = DataManipulation.LinearInterpol(y_vals, x_vals, column)
            elif method == 'cubic':
                new_vals = DataManipulation.CubicInterpol(y_vals, x_vals, column)
            else:
                raise ValueError("Unbekannte Methode in interpol: nutze 'linear' oder 'cubic'.")

            # Das interpolierte Ergebnis ist unsere neue Spalte
            new_column = new_vals
        else:
            # Keine Interpolation: direkte Verwendung des Arrays
            new_column = column

        # 3. Spaltenname festlegen
        if name is None:
            # Nächster Index als String
            next_index = len(df.columns)
            name = str(next_index)

        # 4. Länge prüfen: new_column muss so viele Einträge haben wie df Zeilen
        if new_column.shape[0] != df.shape[0]:
            raise ValueError(
                f"Neue Spalte hat Länge {new_column.shape[0]}, "
                f"muss aber {df.shape[0]} entsprechen."
            )

        # 5. Spalte hinzufügen (inplace)
        df[name] = new_column
        return df
    
    @staticmethod
    def Normalise(df: pd.DataFrame, columns, Arg: str = 'standard') -> pd.DataFrame:
        """
        Normalisiert bestimmte Spalten eines DataFrames nach verschiedenen Methoden.

        Args:
            df (pd.DataFrame): Eingabedaten.
            columns (list[str] | str): Liste der zu normalisierenden Spaltennamen oder '*' für alle Spalten (falls '*' kein Spaltenname ist).
            Arg (str): Optionen:
                - "standard": (default) Mittelwert = 0, Std-Abw = 1
                - "mean": nur Mittelwertzentrierung
                - "start": Startwert auf 0 setzen
                - "amplitude": Skaliere Werte auf [0, 1]

        Returns:
            pd.DataFrame: Neues DataFrame mit normalisierten Spalten.
        """

        df = df.copy()

        # Spaltenauswahl
        if columns == '*' and '*' not in df.columns:
            selected_columns = df.columns
        elif isinstance(columns, str):
            selected_columns = [columns]
        else:
            selected_columns = columns

        for col in selected_columns:
            x = df[col].values.astype(float)

            if Arg == "amplitude":
                min_val = np.min(x)
                max_val = np.max(x)
                if max_val - min_val != 0:
                    x = (x - min_val) / (max_val - min_val)
                else:
                    x[:] = 0.0  # falls konstante Spalte

            elif Arg == "start":
                x = x - x[0]

            elif Arg == "mean":
                x = x - np.mean(x)

            elif Arg == "standard":
                mean = np.mean(x)
                std = np.std(x)
                if std != 0:
                    x = (x - mean) / std
                else:
                    x[:] = 0.0  # falls konstante Spalte

            df[col] = x

        return df