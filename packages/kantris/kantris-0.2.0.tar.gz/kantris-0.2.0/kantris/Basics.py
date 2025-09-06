from typing import Any, Iterable, Union, Optional, Set, List
import numpy as np
import math


class Basics:
    VERSION = 'Kantris.Basics: 0.2.0'
    @staticmethod
    def dictMultiGet(
        data: dict,
        keys: Union[Iterable, tuple, str],
        default: Any = None,
        allow_multikey: bool = True,
        log: bool = True,
        default_None: bool = False
    ) -> Any:
        # Sentinel-Objekt für eindeutige Prüfung
        _MISSING = object()
        if isinstance(keys, str):
            keys = (keys)
        # Liste aller (key, value)-Paare, die im Dict gefunden wurden
        found = [(key, data.get(key, _MISSING)) for key in keys]
        # Filtere nur die existierenden Keys
        valid = [(k, v) for (k, v) in found if v is not _MISSING]
        count = len(valid)

        result = None
        if count == 0:
            result = default

        elif count == 1:
            result = valid[0][1]

        elif count > 1:
            if allow_multikey:
                if log:
                    keys_str = [k for (k, _) in valid]
                    print(f"INFO for Basics.dictMultiGet: Mehrere Keys gefunden: {keys_str}, gebe ersten Wert zurück.")
                result = valid[0][1]
            else:
                if log:
                    keys_str = [k for (k, _) in valid]
                    print(f"ERROR for Basics.dictMultiGet: Mehrere Keys gefunden {keys_str}, 'allow_multikey=False'. Gebe default zurück.")
                result = default
        if result is None and default_None:
            result = default
        return result
    
    @staticmethod
    def dictListFloats(data: dict, n: int = 4):
        String = ''
        for key in data:
            String = String + f'{key}: {Basics.roundFloat(data[key], n)}, '
        return String[:-2]
    
    @staticmethod
    def dictFormattedPrint(dicts, joins: tuple|list = (), keys: tuple|list = None):
        if isinstance(dicts, dict):
            dicts = [dicts, ]
        if isinstance(joins, str):
            joins = [joins, ]
        if len(dicts)-1 != len(joins):
            print(f'ERROR for Basics.dictFormattedPrint: {len(dicts)} dicts given, but only {len(joins)} joins. Need N-1 joins')

        if keys is None:
            keys = set(dicts[0].keys())
        for item in dicts[1:-1]:
            if set(item.keys()) != keys:
                print(f'ERROR for Basics.dictFormattedPrint: All dicts do not have the same Keys')
        
        max_length = max([len(key) for key in keys])
        _MISSING = object()
        for key in keys:
            for i in range(len(dicts)):
                if i == 0:
                    Joined = dicts[i][key]
                else:
                    dict_i_key = dicts[i].get(key, _MISSING)
                    if dict_i_key == _MISSING:
                        continue
                    Joined = f'{Joined} {joins[i-1]} {dict_i_key}'

            print(f'{key}{" " * (max_length - len(key))}: {Joined}')




    @staticmethod
    def roundFloat(x: Union[float, np.floating], sig: int = 4) -> float:
        """
        Rundet x auf 'sig' signifikante Stellen.
        
        Args:
            x: Zahl (float oder np.floating), die gerundet werden soll.
            sig: Anzahl der Signifikanten (default=4).
            
        Returns:
            Gerundeter Wert als Python float.
        """
        if x == np.inf or x == -np.inf:
            return x
        x = float(x)
        if x == 0:
            return 0.0
        # Exponent in Basis 10
        exp = math.floor(math.log10(abs(x)))
        # Anzahl Dezimalstellen, auf die round() angewendet wird
        ndigits = sig - exp - 1
        return round(x, ndigits)
    
    @staticmethod
    def SplitSegments(pts: np.ndarray, max_gap: float) -> List[np.ndarray]:
        """
        Teilt das (M,2)-Array dort auf, wo die Distanz
        zwischen aufeinanderfolgenden Punkten > max_gap ist.
        """
        if pts.shape[0] == 0:
            return []

        # dt = Abstände zwischen aufeinanderfolgenden Punkten
        deltas = np.sqrt(np.sum(np.diff(pts, axis=0)**2, axis=1))
        # Indizes, an denen wir brechen wollen
        breaks = np.nonzero(deltas > max_gap)[0]

        segments = []
        start = 0
        for b in breaks:
            segments.append(pts[start : b+1])
            start = b+1
        # letzte Strecke
        segments.append(pts[start:])
        return segments
    @staticmethod
    def linspaceInteger(min_val, max_val, n):
        """
        Gibt n ganzzahlige Werte mit möglichst gleichem Abstand zwischen min und max zurück.
        
        Parameter:
        ----------
        min_val : int
            Der minimale Wert (inklusive)
        max_val : int
            Der maximale Wert (inklusive)
        n : int
            Anzahl gewünschter Werte

        Rückgabe:
        ---------
        ndarray von int
            n ganzzahlige Werte von min bis max mit möglichst gleichem Abstand
        """
        if n <= 1:
            return np.array([int(round((min_val + max_val) / 2))])
        
        # Erzeuge linspace, dann runde und mache unique
        vals = np.linspace(min_val, max_val, n)
        return np.unique(np.round(vals).astype(int))

class Geometry:
    @staticmethod
    def project_to_plane(data: np.ndarray, basis: np.ndarray) -> np.ndarray:
        """
        Projiziert eine M×N-Datenmenge auf eine 2D-Ebene, definiert durch zwei
        lineare unabhängige N-dimensionale Basisvektoren.

        Args:
            data (np.ndarray): Array der Form (M, N), wobei M die Anzahl der Punkte
                                und N die Dimension ist.
            basis (np.ndarray): Array der Form (N, 2), dessen Spalten die beiden
                                Basisvektoren der Ebene sind.

        Returns:
            np.ndarray: Array der Form (M, 2) mit den Koordinaten der projizierten
                        Punkte in der {basis[:,0], basis[:,1]}-Koordinatenbasis.
        """
        # Prüfen, ob data 2D ist und basis die richtige Form hat
        if data.ndim != 2:
            raise ValueError("`data` muss ein 2D-Array der Form (M, N) sein.")
        M, N = data.shape

        if basis.ndim != 2 or basis.shape != (N, 2):
            raise ValueError("`basis` muss die Form (N, 2) haben, "
                                "mit N = data.shape[1].")

        # Prüfen, dass die beiden Basisvektoren linear unabhängig sind
        if np.linalg.matrix_rank(basis) < 2:
            raise ValueError("Die beiden Basisvektoren müssen linear unabhängig sein.")

        # P ist N×2, Pinv seine Pseudoinverse (2×N)
        P = basis
        Pinv = np.linalg.pinv(P)

        # Daten (M×N) transponieren zu (N×M), dann projizieren zu (2×M)
        coords_2xM = Pinv @ data.T

        # Rückgabe in Form (M×2)
        return coords_2xM.T