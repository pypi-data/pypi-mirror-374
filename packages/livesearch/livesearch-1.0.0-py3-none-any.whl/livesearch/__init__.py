from typing import Any, List, Iterable, Union
import re
from typing import Any, Generic, TypeVar, Optional, Set, Union

DEFAULT_MATCH_CONFIDENCE = 100

T = TypeVar('T')

class SearchPart():
    def __init__(self, search_str: str, weight: float = 1.0):
        self.search_str = search_str
        self.weight = weight

class SearchItem(Generic[T]):
    def __init__(self, search_strs: Union[SearchPart, List[SearchPart], str, List[str]], result_obj: T):
        self.search_parts: List[SearchPart] = []
        if isinstance(search_strs, list):
            if len(search_strs) == 0:
                raise ValueError("search_strs list cannot be empty")
            if isinstance(search_strs[0], str):
                self.search_parts = [SearchPart(s, 1.0) for s in search_strs]
            else:
                self.search_parts = search_strs
        elif isinstance(search_strs, str):
            self.search_parts = [SearchPart(search_strs, 1.0)]
        elif isinstance(search_strs, SearchPart):
            self.search_parts = [search_strs]
        else:
            raise ValueError("search_strs must be a string, a list of strings, a SearchPart, or a list of SearchParts")
        self.result_obj: T = result_obj

    def get_obj(self) -> T:
        return self.result_obj

    def __eq__(self, value):
        if not isinstance(value, SearchItem):
            return NotImplemented
        return self.result_obj == value.result_obj

    def __hash__(self):
        return hash(self.result_obj)

class SearchResult(Generic[T]):
    def __init__(self, item: SearchItem[T], confidence: float):
        self.item = item
        self.confidence = confidence

    def __eq__(self, value: "SearchResult[T]"):
        if not isinstance(value, SearchResult):
            return NotImplemented
        return self.item == value.item

    def __hash__(self):
        return hash(self.item)

    def get_obj(self) -> T:
        return self.item.get_obj()

    def get_confidence(self) -> float:
        return self.confidence

    def get_item(self) -> SearchItem[T]:
        return self.item

    @staticmethod
    def _sort_detector_result_list(detector_result_list: List['SearchResult']):
        return sorted(detector_result_list, key=lambda x: x.confidence, reverse=True)


class Detector:
    def get_results(self, lookfor: str, lookin: Iterable[SearchItem[T]]) -> List[SearchResult[T]]:
        return []


class BeginningMatch(Detector):
    # If we match at the beginning, we double the confidence
    confidence = DEFAULT_MATCH_CONFIDENCE * 2

    def get_results(self, lookfor: str, lookin: Iterable[SearchItem[T]]) -> List[SearchResult[T]]:
        pattern = re.compile(r'^' + lookfor, re.IGNORECASE)
        ret = []
        for look in lookin:
            for part in look.search_parts:
                if pattern.match(part.search_str):
                    ret.append(SearchResult(look, confidence=self.confidence * part.weight))
        return ret


class FullMatch(Detector):
    # A full match is just normal confidence
    confidence = DEFAULT_MATCH_CONFIDENCE

    def get_results(self, lookfor: str, lookin: Iterable[SearchItem[T]]) -> List[SearchResult[T]]:
        pattern = re.compile(lookfor, re.IGNORECASE)
        ret = []
        for look in lookin:
            for part in look.search_parts:
                match = pattern.findall(part.search_str)
                if len(match) > 0:
                    ret.append(SearchResult(look, confidence=self.confidence + (DEFAULT_MATCH_CONFIDENCE/10) * len(match) * part.weight))
        return ret


class PartsMatch(Detector):
    # Parts matching is kinda lame, but it might work for some cases
    confidence = DEFAULT_MATCH_CONFIDENCE / 4
    def __init__(self, char_split: str = " "):
        self.char_split = char_split

    def get_results(self, lookfor: str, lookin: Iterable[SearchItem[T]]) -> List[SearchResult[T]]:
        allSearch = lookfor.strip().split(self.char_split)
        ret = []
        averageLength = sum(len(s) for s in allSearch) / len(allSearch) if len(allSearch) > 0 else 0
        for item in lookin:
            for search_part in item.search_parts:
                item_confidence = 0
                for search in allSearch:
                    pattern = re.compile(re.escape(search), re.IGNORECASE)
                    if pattern.search(search_part.search_str):
                        item_confidence += self.confidence * search_part.weight * (len(search) / averageLength if averageLength > 0 else 1)
                if item_confidence > 0:
                    ret.append(SearchResult(item, confidence=item_confidence))
        return ret

DEFAULT_DETECTORS: List[Detector] = [
    BeginningMatch(),
    FullMatch(),
    PartsMatch(" ")
]

def search_get_details(string: str, stringlist: Iterable[SearchItem[T]], detectors: List[Detector]) -> List[SearchResult[T]]:
    results = []
    """Search for a string in an iterable and return the first match."""
    for detector in detectors:
        results.append(detector.get_results(string, stringlist))

    # Coalesce the results into a single list. Remove duplicates from detectors, and add confidence numbers together
    from typing import Dict
    uniqueMatches: Dict[SearchResult[T], SearchResult[T]] = {}
    for i in range(len(detectors)):
        currentList: List[SearchResult[T]] = results[i]
        for normalMatch in currentList:
            if normalMatch not in uniqueMatches:
                uniqueMatches[normalMatch] = normalMatch
            else:
                print("Merging confidence for", normalMatch.get_obj())
                uniqueMatches[normalMatch].confidence += normalMatch.confidence

    # Sort the results by confidence
    uniqueMatches = SearchResult._sort_detector_result_list(list(uniqueMatches.values()))

    return uniqueMatches

def search_strings(string: str, search_list: List[str], detectors: List[Detector] = DEFAULT_DETECTORS) -> List[SearchResult[str]]:
    wrapped_list: List[SearchItem[str]] = [SearchItem(s, s) for s in search_list]
    results: List[SearchResult[str]] = search_get_details(string, wrapped_list, detectors)
    return results

def search_items(string: str, search_list: List[SearchItem[T]], detectors: List[Detector] = DEFAULT_DETECTORS) -> List[SearchResult[T]]:
    if len(search_list) > 0:
        if not isinstance(search_list[0], SearchItem):
            raise ValueError("search_list must be a list of SearchItem objects")
    return search_get_details(string, search_list, detectors)
