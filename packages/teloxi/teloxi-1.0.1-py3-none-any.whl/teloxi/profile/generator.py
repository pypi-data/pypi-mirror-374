import json, random
from pathlib import Path
from functools import lru_cache

BASE_DIR = Path(__file__).resolve().parent

class Name:
    def __init__(self, name_data: dict):
        self.en_name    = name_data.get('en_name')
        self.fa_name    = name_data.get('fa_name')
        self.fa_surname = name_data.get('fa_surname')
        self.en_surname = name_data.get('en_surname')
        self.gender     = name_data.get('gender')
        self.persian    = name_data.get('persian')
        
    
    def to_dict(self):
        return {
            "en_name": self.en_name,
            "fa_name": self.fa_name,
            "en_surname": self.en_surname,
            "fa_surname": self.fa_surname,
            "gender": self.gender,
            "persian": self.persian
        }

    def __repr__(self):
        return f"Name({self.to_dict()})"
    def __str__(self):
        return f"{self.en_name} {self.en_surname}"

class NameGenerator:
    def __init__(self):
        pass

    def get_name(self, gender: str | None = 'male', persian: bool | None = False):
        gender = gender if gender in ['male', 'female'] else random.choice(['male', 'female'])
        persian = persian if isinstance(persian, bool) else random.choice([True, False])

        data = self._persian_names() if persian else self._universal_names()

        try:
            name = random.choice(data[gender])
            surname = random.choice(data['surname'])
        except (KeyError, IndexError) as e:
            raise ValueError(f"Error generating name: {e}")

        result = {
            "en_name": name.get('en'),
            "fa_name": name.get('fa'),
            "en_surname": surname.get('en'),
            "fa_surname": surname.get('fa'),
            "gender": gender,
            "persian": persian
        }

        return Name(result)

    @lru_cache()
    def _persian_names(self) -> dict:
        return self._load_json(BASE_DIR / 'persian_names.json')

    @lru_cache()
    def _universal_names(self) -> dict:
        return self._load_json(BASE_DIR / 'universal_names.json')

    def _load_json(self, path: Path) -> dict:
        try:
            with path.open(encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"file not found: {path}")
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding JSON: {path}")



class NameFactory:
    
    _generator = NameGenerator()

    @classmethod
    def generate(cls, gender: str | None = None, persian: bool | None = False) -> Name:
        return cls._generator.get_name(gender, persian)

    
    
    @classmethod
    def generate_female(cls, persian: bool | None = None) -> Name:
        return cls.generate('female', persian)

    @classmethod
    def generate_male(cls, persian: bool | None =  None) -> Name:
        return cls.generate('male', persian)
    
    @classmethod
    def generate_random(cls, persian: bool | None = None) -> Name:
        return cls.generate(None, persian)