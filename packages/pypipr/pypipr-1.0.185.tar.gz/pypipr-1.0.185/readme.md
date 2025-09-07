
# About
The Python Package Index Project (pypipr)

pypi : https://pypi.org/project/pypipr


# Setup
Install with pip
```
pip install pypipr
```

Then import pypipr
```python
from pypipr import *
# or
import pypipr
```

Or run in terminal/console/cmd/bash
```cmd
pypipr
```

# CONSTANT

`LINUX`

`PintUreg`

`WINDOWS`

# FUNCTION

## avg

`avg(i)`

Simple Average Function karena tidak disediakan oleh python  
  
```python  
n = [1, 22, 2, 3, 13, 2, 123, 12, 31, 2, 2, 12, 2, 1]  
print(avg(n))  
```

Output:
```py
16.285714285714285
```

## get_filemtime

`get_filemtime(filename)`

Mengambil informasi last modification time file dalam nano seconds  
  
```python  
print(get_filemtime(__file__))  
```

Output:
```py
1746618872356961296
```

## print_colorize

`print_colorize(text, color='\x1b[32m', bright='\x1b[1m', color_end='\x1b[0m', text_start='', text_end='\n', delay=0.05)`

Print text dengan warna untuk menunjukan text penting  
  
```py  
print_colorize("Print some text")  
print_colorize("Print some text", color=colorama.Fore.RED)  
```

## print_log

`print_log(text)`

Akan melakukan print ke console.  
Berguna untuk memberikan informasi proses program yg sedang berjalan.  
  
```python  
print_log("Standalone Log")  
```

Output:
```py
[32m[1m>>> Standalone Log[0m
```

## console_run

`console_run(info, command=None, print_info=True, capture_output=False)`

Menjalankan command seperti menjalankan command di Command Terminal  
  
```py  
console_run('dir')  
console_run('ls')  
```

## auto_reload

`auto_reload(filename)`

Menjalankan file python secara berulang.  
Dengan tujuan untuk melihat perubahan secara langsung.  
Pastikan kode aman untuk dijalankan.  
Jalankan kode ini di terminal console.  
  
```py  
auto_reload("file_name.py")  
```  
  
or run in terminal  
  
```  
pypipr auto_reload  
```

## basename

`basename(path)`

Mengembalikan nama file dari path  
  
```python  
print(basename("/ini/nama/folder/ke/file.py"))  
```

Output:
```py
file.py
```

## chr_to_int

`chr_to_int(s, start=0, numbers='abcdefghijklmnopqrstuvwxyz')`

Fungsi ini berguna untuk mengubah urutan huruf menjadi angka.  
  
```python  
print(chr_to_int('z'))  # Output: 26  
print(chr_to_int('aa'))  # Output: 27  
print(chr_to_int('abc', numbers="abc"))  # Output: 18  
```

Output:
```py
25
26
17
```

## int_to_chr

`int_to_chr(n, start=0, numbers='abcdefghijklmnopqrstuvwxyz')`

Fungsi ini berguna untuk membuat urutan dari huruf.  
Seperti a, b, ...., z, aa, bb, ....  
  
```python  
for i in range(30):  
    print(f"{i} = {int_to_chr(i)}")  
  
print(int_to_chr(7777))  
```

Output:
```py
0 = a
1 = b
2 = c
3 = d
4 = e
5 = f
6 = g
7 = h
8 = i
9 = j
10 = k
11 = l
12 = m
13 = n
14 = o
15 = p
16 = q
17 = r
18 = s
19 = t
20 = u
21 = v
22 = w
23 = x
24 = y
25 = z
26 = aa
27 = ab
28 = ac
29 = ad
kmd
```

## irange

`irange(start, stop=None, step=None, index=0, numbers=None, outer=False)`

Meningkatkan fungsi range() dari python untuk pengulangan menggunakan huruf  
  
```python  
print(irange(10))  
print(irange(3, 15))  
iprint(irange(13, 5))  
iprint(irange(2, 10, 3))  
iprint(irange(2, '10', 3))  
iprint(irange('10'))  
iprint(irange('10', '100', 7))  
iprint(irange("h"))  
iprint(irange("A", "D"))  
iprint(irange("z", "a", 4))  
```

Output:
```py
<generator object int_range at 0x7eed66cc40>
<generator object int_range at 0x7eed66cc40>
[13, 12, 11, 10, 9, 8, 7, 6]
[2, 5, 8]
[2, 5, 8]
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
[10, 17, 24, 31, 38, 45, 52, 59, 66, 73, 80, 87, 94]
['a', 'b', 'c', 'd', 'e', 'f', 'g']
['A', 'B', 'C']
['z', 'v', 'r', 'n', 'j', 'f', 'b']
```

## batchmaker

`batchmaker(pattern: str)`

Alat Bantu untuk membuat teks yang berulang.  
Gunakan `{[start][separator][finish]([separator][step])}`.  
```  
[start] dan [finish]    -> bisa berupa huruf maupun angka  
([separator][step])     -> bersifat optional  
[separator]             -> selain huruf dan angka  
[step]                  -> berupa angka positif  
```  
  
```python  
s = "Urutan {1/6/3} dan {10:9} dan {j k} dan {Z - A - 15} saja."  
print(batchmaker(s))  
print(list(batchmaker(s)))  
```

Output:
```py
<generator object batchmaker at 0x7eed641d80>
['Urutan 1 dan 10 dan j dan Z saja.', 'Urutan 1 dan 10 dan j dan K saja.', 'Urutan 1 dan 10 dan j dan  saja.', 'Urutan 1 dan 10 dan k dan Z saja.', 'Urutan 1 dan 10 dan k dan K saja.', 'Urutan 1 dan 10 dan k dan  saja.', 'Urutan 1 dan 9 dan j dan Z saja.', 'Urutan 1 dan 9 dan j dan K saja.', 'Urutan 1 dan 9 dan j dan  saja.', 'Urutan 1 dan 9 dan k dan Z saja.', 'Urutan 1 dan 9 dan k dan K saja.', 'Urutan 1 dan 9 dan k dan  saja.', 'Urutan 4 dan 10 dan j dan Z saja.', 'Urutan 4 dan 10 dan j dan K saja.', 'Urutan 4 dan 10 dan j dan  saja.', 'Urutan 4 dan 10 dan k dan Z saja.', 'Urutan 4 dan 10 dan k dan K saja.', 'Urutan 4 dan 10 dan k dan  saja.', 'Urutan 4 dan 9 dan j dan Z saja.', 'Urutan 4 dan 9 dan j dan K saja.', 'Urutan 4 dan 9 dan j dan  saja.', 'Urutan 4 dan 9 dan k dan Z saja.', 'Urutan 4 dan 9 dan k dan K saja.', 'Urutan 4 dan 9 dan k dan  saja.', 'Urutan 7 dan 10 dan j dan Z saja.', 'Urutan 7 dan 10 dan j dan K saja.', 'Urutan 7 dan 10 dan j dan  saja.', 'Urutan 7 dan 10 dan k dan Z saja.', 'Urutan 7 dan 10 dan k dan K saja.', 'Urutan 7 dan 10 dan k dan  saja.', 'Urutan 7 dan 9 dan j dan Z saja.', 'Urutan 7 dan 9 dan j dan K saja.', 'Urutan 7 dan 9 dan j dan  saja.', 'Urutan 7 dan 9 dan k dan Z saja.', 'Urutan 7 dan 9 dan k dan K saja.', 'Urutan 7 dan 9 dan k dan  saja.']
```

## calculate

`calculate(teks)`

Mengembalikan hasil dari perhitungan teks menggunakan modul pint.  
Mendukung perhitungan matematika dasar dengan satuan.  
  
Return value:  
- Berupa class Quantity dari modul pint  
  
Format:  
- f"{result:~P}"            -> pretty  
- f"{result:~H}"            -> html  
- result.to_base_units()    -> SI  
- result.to_compact()       -> human readable  
  
```python  
fx = "3 meter * 10 cm * 3 km"  
res = calculate(fx)  
print(res)  
print(res.to_base_units())  
print(res.to_compact())  
print(f"{res:~P}")  
print(f"{res:~H}")  
```

Output:
```py
90 centimeter * kilometer * meter
900.0 meter ** 3
900.0 meter ** 3
90 cm·km·m
90 cm km m
```

## batch_calculate

`batch_calculate(pattern)`

Analisa perhitungan massal.  
Bisa digunakan untuk mencari alternatif terendah/tertinggi/dsb.  
  
  
```python  
print(batch_calculate("{1 10} m ** {1 3}"))  
print(list(batch_calculate("{1 10} m ** {1 3}")))  
```

Output:
```py
<generator object batch_calculate at 0x7eed6892a0>
[('1 m ** 1', <Quantity(1, 'meter')>), ('1 m ** 2', <Quantity(1, 'meter ** 2')>), ('1 m ** 3', <Quantity(1, 'meter ** 3')>), ('2 m ** 1', <Quantity(2, 'meter')>), ('2 m ** 2', <Quantity(2, 'meter ** 2')>), ('2 m ** 3', <Quantity(2, 'meter ** 3')>), ('3 m ** 1', <Quantity(3, 'meter')>), ('3 m ** 2', <Quantity(3, 'meter ** 2')>), ('3 m ** 3', <Quantity(3, 'meter ** 3')>), ('4 m ** 1', <Quantity(4, 'meter')>), ('4 m ** 2', <Quantity(4, 'meter ** 2')>), ('4 m ** 3', <Quantity(4, 'meter ** 3')>), ('5 m ** 1', <Quantity(5, 'meter')>), ('5 m ** 2', <Quantity(5, 'meter ** 2')>), ('5 m ** 3', <Quantity(5, 'meter ** 3')>), ('6 m ** 1', <Quantity(6, 'meter')>), ('6 m ** 2', <Quantity(6, 'meter ** 2')>), ('6 m ** 3', <Quantity(6, 'meter ** 3')>), ('7 m ** 1', <Quantity(7, 'meter')>), ('7 m ** 2', <Quantity(7, 'meter ** 2')>), ('7 m ** 3', <Quantity(7, 'meter ** 3')>), ('8 m ** 1', <Quantity(8, 'meter')>), ('8 m ** 2', <Quantity(8, 'meter ** 2')>), ('8 m ** 3', <Quantity(8, 'meter ** 3')>), ('9 m ** 1', <Quantity(9, 'meter')>), ('9 m ** 2', <Quantity(9, 'meter ** 2')>), ('9 m ** 3', <Quantity(9, 'meter ** 3')>), ('10 m ** 1', <Quantity(10, 'meter')>), ('10 m ** 2', <Quantity(10, 'meter ** 2')>), ('10 m ** 3', <Quantity(10, 'meter ** 3')>)]
```

## bin_to_int

`bin_to_int(n)`

Fungsi ini berguna untuk mengubah angka binary  
menjadi angka integer.  
  
```python  
print(bin_to_int(bin(244)))  
```

Output:
```py
244
```

## is_empty

`is_empty(variable)`

Versi cepat dan aman dari is_empty sesuai himpunan "kosong" yang Anda definisikan:  
  - None  
  - False  
  - Angka 0 (termasuk -0.0)  
  - String: "0", "", "-0", "\n", "\t"  
  - Koleksi kosong: list(), tuple(), dict(), set()

## exit_if_empty

`exit_if_empty(*args)`

Keluar dari program apabila seluruh variabel  
setara dengan empty  
  
```py  
var1 = None  
var2 = '0'  
exit_if_empty(var1, var2)  
```

## input_char

`input_char(prompt=None, prompt_ending='', newline_after_input=True, echo_char=True, default=None, color=None)`

Meminta masukan satu huruf tanpa menekan Enter.  
  
```py  
input_char("Input char : ")  
input_char("Input char : ", default='Y')  
input_char("Input Char without print : ", echo_char=False)  
```

## choices

`choices(daftar, contains=None, prompt='Choose : ')`

Memudahkan dalam membuat pilihan untuk user dalam tampilan console  
  
```py  
var = {  
    "Pertama" : "Pilihan Pertama",  
    "Kedua" : "Pilihan Kedua",  
    "Ketiga" : "Pilihan Ketiga",  
}  
res = choices(  
    var,  
    prompt="Pilih dari dictionary : "  
)  
print(res)  
```

## chunk_array

`chunk_array(array, size, start=0)`

Membagi array menjadi potongan-potongan dengan besaran yg diinginkan  
  
```python  
arr = [2, 3, 12, 3, 3, 42, 42, 1, 43, 2, 42, 41, 4, 24, 32, 42, 3, 12, 32, 42, 42]  
print(chunk_array(arr, 5))  
print(list(chunk_array(arr, 5)))  
```

Output:
```py
<generator object chunk_array at 0x7eed670b80>
[[2, 3, 12, 3, 3], [42, 42, 1, 43, 2], [42, 41, 4, 24, 32], [42, 3, 12, 32, 42], [42]]
```

## create_folder

`create_folder(folder_name, wait_until_success=True)`

Membuat folder.  
Membuat folder secara recursive dengan permission.  
  
```py  
create_folder("contoh_membuat_folder")  
create_folder("contoh/membuat/folder/recursive")  
create_folder("./contoh_membuat_folder/secara/recursive")  
```

## datetime_from_string

`datetime_from_string(iso_string, timezone='UTC')`

Parse iso_string menjadi datetime object  
  
```python  
print(datetime_from_string("2022-12-12 15:40:13").isoformat())  
print(datetime_from_string(  
    "2022-12-12 15:40:13",  
    timezone="Asia/Jakarta"  
).isoformat())  
```

Output:
```py
2022-12-12T15:40:13+00:00
2022-12-12T15:40:13+07:00
```

## datetime_now

`datetime_now(timezone=None)`

Memudahkan dalam membuat Datetime untuk suatu timezone tertentu  
  
```python  
print(datetime_now("Asia/Jakarta"))  
print(datetime_now("GMT"))  
print(datetime_now("Etc/GMT+7"))  
```

Output:
```py
2025-09-07 14:25:43.464503+07:00
2025-09-07 07:25:43.466355+00:00
2025-09-07 00:25:43.471155-07:00
```

## dict_first

`dict_first(d: dict, remove=False)`

Mengambil nilai (key, value) pertama dari dictionary dalam bentuk tuple.  
  
```python  
d = {  
    "key2": "value2",  
    "key3": "value3",  
    "key1": "value1",  
}  
print(dict_first(d, remove=True))  
print(dict_first(d))  
```

Output:
```py
('key2', 'value2')
('key3', 'value3')
```

## traceback_filename

`traceback_filename(stack_level=-3)`

Mendapatkan filename dimana fungsi yg memanggil  
fungsi dimana fungsi ini diletakkan dipanggil.  
  
```py  
print(traceback_filename())  
```

## dirname

`dirname(path=None, indeks=-2)`

## dirpath

`dirpath(path, indeks=-1, abs_path=None)`

Mengembalikan bagian direktori dari sebuah path berdasarkan indeks.  
Tanpa trailing slash di akhir.  
  
Args:  
    path (str): Path lengkap ke file atau direktori.  
    indeks (int): Indeks negatif untuk menentukan seberapa jauh naik ke atas direktori.  
    abs_path (bool | None):  
        - True untuk path absolut,  
        - False untuk path relatif terhadap cwd,  
        - None untuk path sesuai pemotongan manual.  
  
Returns:  
    str: Path direktori hasil ekstraksi.  
  
Contoh:  
    dirpath("/a/b/c/d/e.txt", -2) -> "a/b/c"

## django_clear_migrations

`django_clear_migrations(appname)`

## django_runserver

`django_runserver()`

## is_iterable

`is_iterable(var, str_is_iterable=False)`

Mengecek apakah suatu variabel bisa dilakukan forloop atau tidak  
  
```python  
s = 'ini string'  
print(is_iterable(s))  
  
l = [12,21,2,1]  
print(is_iterable(l))  
  
r = range(100)  
print(is_iterable(r))  
  
d = {'a':1, 'b':2}  
print(is_iterable(d.values()))  
```

Output:
```py
False
True
True
True
```

## to_str

`to_str(value)`

Mengubah value menjadi string literal yang konsisten.  
  
Aturan:  
- str: dikembalikan apa adanya.  
- bool: True -> "1", False -> "0".  
- int/float: dikonversi via str().  
- None atau objek kosong (menurut is_empty): "".  
- fallback: str(value), atau TypeError jika gagal.

## filter_empty

`filter_empty(iterable, *, zero_is_empty: bool = True, false_is_empty: bool = True, str_strip: bool = True, string_not_iterable: bool = True, drop_none: bool = True, drop_nan: bool = True, drop_empty_iterables: bool = True, drop_empty_mappings: bool = True)`

Generator yang mengembalikan elemen non-kosong dari iterable.  
Lihat docstring sebelumnya untuk detail parameter.

## get_by_index

`get_by_index(obj, index, on_error=None)`

Mendapatkan value dari object berdasarkan indexnya.  
Jika error out of range maka akan mengembalikan on_error.  
  
```python  
l = [1, 3, 5]  
print(get_by_index(l, 7))  
```

Output:
```py
None
```

## get_class_method

`get_class_method(cls)`

Mengembalikan berupa tuple yg berisi list dari method dalam class  
  
```python  
class ExampleGetClassMethod:  
    def a():  
        return [x for x in range(10)]  
  
    def b():  
        return [x for x in range(10)]  
  
    def c():  
        return [x for x in range(10)]  
  
    def d():  
        return [x for x in range(10)]  
  
print(get_class_method(ExampleGetClassMethod))  
print(list(get_class_method(ExampleGetClassMethod)))  
```

Output:
```py
<generator object get_class_method at 0x7eed689540>
[<function ExampleGetClassMethod.a at 0x7eed6a1620>, <function ExampleGetClassMethod.b at 0x7eed6a1080>, <function ExampleGetClassMethod.c at 0x7eed6a1120>, <function ExampleGetClassMethod.d at 0x7eed6a14e0>]
```

## get_filesize

`get_filesize(filename)`

Mengambil informasi file size dalam bytes  
  
```python  
print(get_filesize(__file__))  
```

Output:
```py
465
```

## github_init

`github_init()`

Menyiapkan folder offline untuk dikoneksikan ke repository  
kosong github.  
Akan langsung di upload dan di taruh di branch main.  
  
  
```py  
github_init()  
```  
  
or run in terminal  
  
```py  
pypipr github_init  
```

## github_pull

`github_pull()`

Menjalankan command `git pull`  
  
```py  
github_pull()  
```

## github_push

`github_push(commit_msg=None)`

Menjalankan command status, add, commit dan push  
  
```py  
github_push('Commit Message')  
```

## github_user

`github_user(email=None, name=None)`

Menyimpan email dan nama user secara global sehingga tidak perlu  
menginput nya setiap saat.  
  
```py  
github_user('my@emil.com', 'MyName')  
```

## hex_to_int

`hex_to_int(n)`

Fungsi ini berguna untuk mengubah angka hexadecimal  
menjadi angka integer.  
  
```python  
print(hex_to_int(hex(244)))  
```

Output:
```py
244
```

## iargv

`iargv(key: int, cast=None, on_error=None)`

Mengambil parameter input dari terminal tanpa menimbulkan error  
apabila parameter kosong.  
Parameter yg berupa string juga dapat diubah menggunakan cast.  
  
```python  
print(iargv(1, cast=int, on_error=100))  
```

Output:
```py
100
```

## idir

`idir(obj, skip_underscore=True)`

Sama seperti dir() python, tetapi skip underscore  
  
```python  
iprint(idir(__import__('pypipr')))  
```

Output:
```py
['ComparePerformance',
 'LINUX',
 'PintUreg',
 'PintUregQuantity',
 'RunParallel',
 'WINDOWS',
 'asyncio',
 'auto_reload',
 'avg',
 'basename',
 'batch_calculate',
 'batchmaker',
 'bin_to_int',
 'calculate',
 'choices',
 'chr_to_int',
 'chunk_array',
 'colorama',
 'console_run',
 'create_folder',
 'csv',
 'datetime',
 'datetime_from_string',
 'datetime_now',
 'dict_first',
 'dirname',
 'dirpath',
 'django_clear_migrations',
 'django_runserver',
 'exit_if_empty',
 'filter_empty',
 'functools',
 'get_by_index',
 'get_class_method',
 'get_filemtime',
 'get_filesize',
 'github_init',
 'github_pull',
 'github_push',
 'github_user',
 'hex_to_int',
 'iargv',
 'idir',
 'idumps',
 'idumps_html',
 'ienumerate',
 'ienv',
 'iexec',
 'iinput',
 'ijoin',
 'iloads',
 'iloads_html',
 'input_char',
 'inspect',
 'int_to_bin',
 'int_to_chr',
 'int_to_hex',
 'int_to_int',
 'int_to_oct',
 'io',
 'iopen',
 'iprint',
 'irange',
 'ireplace',
 'is_empty',
 'is_file_exist',
 'is_html',
 'is_iterable',
 'is_raw_string',
 'is_valid_url',
 'iscandir',
 'isplit',
 'ivars',
 'json',
 'log',
 'lxml',
 'math',
 'multiprocessing',
 'no_indent',
 'oct_to_int',
 'operator',
 'os',
 'password_generator',
 'path_to_module',
 'pathlib',
 'pint',
 'pip_freeze_without_version',
 'pip_update_pypipr',
 'poetry_publish',
 'poetry_shell',
 'poetry_update_version',
 'pprint',
 'print_colorize',
 'print_dir',
 'print_log',
 'print_to_last_line',
 'queue',
 'random',
 'random_bool',
 're',
 'repath',
 'requests',
 'restart',
 'set_timeout',
 'sets_ordered',
 'sqlite_backup',
 'sqlite_delete_table',
 'sqlite_get_all_tables',
 'sqlite_get_data_table',
 'str_cmp',
 'string',
 'subprocess',
 'sys',
 'text_colorize',
 'textwrap',
 'threading',
 'tiles',
 'time',
 'to_str',
 'traceback',
 'traceback_filename',
 'traceback_framename',
 'tzdata',
 'uuid',
 'webbrowser',
 'yaml',
 'zoneinfo']
```

## idumps_html

`idumps_html(data, indent=None)`

Serialisasi python variabel menjadi HTML.  
  
```html  
List -> <ul>...</ul>  
Dict -> <table>...</table>  
```  
  
```python  
data = {  
    'abc': 123,  
    'list': [1, 2, 3, 4, 5],  
    'dict': {'a': 1, 'b':2, 'c':3},  
}  
print(idumps_html(data))  
```

Output:
```py
<table>
  <tbody>
    <tr>
      <th>abc</th>
      <td>
        <span>123</span>
      </td>
    </tr>
    <tr>
      <th>list</th>
      <td>
        <ul>
          <li>
            <span>1</span>
          </li>
          <li>
            <span>2</span>
          </li>
          <li>
            <span>3</span>
          </li>
          <li>
            <span>4</span>
          </li>
          <li>
            <span>5</span>
          </li>
        </ul>
      </td>
    </tr>
    <tr>
      <th>dict</th>
      <td>
        <table>
          <tbody>
            <tr>
              <th>a</th>
              <td>
                <span>1</span>
              </td>
            </tr>
            <tr>
              <th>b</th>
              <td>
                <span>2</span>
              </td>
            </tr>
            <tr>
              <th>c</th>
              <td>
                <span>3</span>
              </td>
            </tr>
          </tbody>
        </table>
      </td>
    </tr>
  </tbody>
</table>

```

## idumps

`idumps(data, syntax='yaml', indent=4)`

Mengubah variabel data menjadi string untuk yang dapat dibaca untuk disimpan.  
String yang dihasilkan berbentuk syntax YAML/JSON/HTML.  
  
```python  
data = {  
    'a': 123,  
    't': ['disini', 'senang', 'disana', 'senang'],  
    'l': (12, 23, [12, 42]),  
}  
print(idumps(data))  
print(idumps(data, syntax='html'))  
```

Output:
```py
a: 123
l: !!python/tuple
- 12
- 23
-   - 12
    - 42
t:
- disini
- senang
- disana
- senang

<table>
    <tbody>
        <tr>
            <th>a</th>
            <td>
                <span>123</span>
            </td>
        </tr>
        <tr>
            <th>t</th>
            <td>
                <ul>
                    <li>
                        <span>disini</span>
                    </li>
                    <li>
                        <span>senang</span>
                    </li>
                    <li>
                        <span>disana</span>
                    </li>
                    <li>
                        <span>senang</span>
                    </li>
                </ul>
            </td>
        </tr>
        <tr>
            <th>l</th>
            <td>
                <ul>
                    <li>
                        <span>12</span>
                    </li>
                    <li>
                        <span>23</span>
                    </li>
                    <li>
                        <ul>
                            <li>
                                <span>12</span>
                            </li>
                            <li>
                                <span>42</span>
                            </li>
                        </ul>
                    </li>
                </ul>
            </td>
        </tr>
    </tbody>
</table>

```

## int_to_int

`int_to_int(n)`

Fungsi ini sama seperti fungsi int().  
fungsi ini dibuat hanya untuk keperluan pembuatan module semata.  
  
```python  
print(int_to_int(7777))  
```

Output:
```py
7777
```

## ienumerate

`ienumerate(iterator, start=0, key=<function int_to_int at 0x7ef2fe20c0>)`

meningkatkan fungsi enumerate() pada python  
untuk key menggunakan huruf dan basis angka lainnya.  
  
```python  
it = ["ini", "contoh", "enumerator"]  
print(ienumerate(it))  
iprint(ienumerate(it, key=int_to_chr))  
```

Output:
```py
<generator object ienumerate at 0x7eed670b80>
[('a', 'ini'), ('b', 'contoh'), ('c', 'enumerator')]
```

## ienv

`ienv(on_windows=None, on_linux=None)`

Mengambalikan hasil berdasarkan environment dimana program dijalankan  
  
```py  
getch = __import__(ienv(on_windows="msvcrt", on_linux="getch"))  
  
  
f = ienv(on_windows=fwin, on_linux=flin)  
f()  
  
  
inherit = ienv(  
    on_windows=[BaseForWindows, BaseEnv, object],  
    on_linux=[SpecialForLinux, BaseForLinux, BaseEnv, object]  
)  
  
class ExampleIEnv(*inherit):  
    pass  
```

## iexec

`iexec(python_syntax, import_pypipr=True)`

improve exec() python function untuk mendapatkan outputnya  
  
```python  
print(iexec('print(9*9)'))  
```

Output:
```py
81

```

## iinput

`iinput(*args, **kwargs)`

iinput()  
iinput("pesan")  
iinput("pesan", default)  
iinput(msg="...", default="...")  
iinput(default="...")

## ijoin

`ijoin(iterable: Any, separator: Any = '', start: str = '', end: str = '', remove_empty: bool = False, recursive: bool = True, recursive_flat: bool = False, str_strip: bool = False, *, dict_mode: Literal['values', 'keys', 'items'] = 'values', string_not_iterable: bool = True) -> str`

Versi cepat & dapat dikonfigurasi dari ijoin.  
  
Parameters  
----------  
iterable : Any  
    Sumber data; jika bukan iterable maka diperlakukan sebagai satu elemen.  
separator : Any  
    Pemisah antar elemen (akan di-cast ke str).  
start, end : str  
    Prefiks & sufiks hasil akhir (pembungkus).  
remove_empty : bool  
    Jika True, elemen kosong (sesuai filter_empty) dibuang.  
recursive : bool  
    Jika True, struktur bersarang diproses rekursif.  
recursive_flat : bool  
    Jika True, level dalam **tidak** memakai start/end (hanya join).  
    Jika False, level dalam ikut memakai start/end (perilaku lama).  
str_strip : bool  
    Jika True, setiap elemen di-strip() setelah to_str.  
dict_mode : {'values','keys','items'}  
    Cara menangani dict: pakai values/keys/items.  
    Untuk 'items', setiap item jadi "key=value" (lihat _item_to_str()).  
string_not_iterable : bool  
    Jika True, str/bytes **tidak** diperlakukan sebagai iterable (aman).  
  
Returns  
-------  
str  
    String gabungan.  
  
Catatan performa  
----------------  
Menggunakan strategi "kumpulkan bagian → 'separator'.join(parts)" agar  
kompleksitas waktu mendekati O(n) dan menghindari O(n²) dari '+='.

## iloads_html

`iloads_html(html)`

Mengambil data yang berupa list `<ul>`, dan table `<table>` dari html  
dan menjadikannya data python berupa list.  
setiap data yang ditemukan akan dibungkus dengan tuple sebagai separator.  
  
```  
list (<ul>)     -> list         -> list satu dimensi  
table (<table>) -> list[list]   -> list satu dimensi didalam list  
```  
  
apabila data berupa ul maka dapat dicek type(data) -> html_ul  
apabila data berupa ol maka dapat dicek type(data) -> html_ol  
apabila data berupa dl maka dapat dicek type(data) -> html_dl  
apabila data berupa table maka dapat dicek type(data) -> html_table  
  
```python  
import pprint  
pprint.pprint(iloads_html(iopen("https://harga-emas.org/")), depth=10)  
pprint.pprint(iloads_html(iopen("https://harga-emas.org/1-gram/")), depth=10)  
```

Output:
```py
([['Satuan', 'USD', 'IDR'],
  ['Ounce (oz)', '3.586,76(0)', '58.746.340,28(0)'],
  ['Gram (gr)', '115,32(0)', '1.888.738,7(0)'],
  ['Kilogram (kg)', '115.317,01(0)', '1.888.738.700(0)']],
 [['Satuan', 'Antam', 'Pegadaian'],
  ['Gram', 'per Gram (Rp)', 'per Gram (Rp)'],
  ['1000', '2.000.600.000', '1.990.105.000'],
  ['500', '1.000.320.000', '995.053.000'],
  ['250', '500.265.000', '497.772.000'],
  ['100', '200.212.000', '199.207.000'],
  ['50', '100.145.000', '99.653.000'],
  ['25', '50.112.000', '49.867.000'],
  ['10', '21.100.000', '19.996.000'],
  ['5', '10.910.000', '10.025.000'],
  ['2', '4.060.000', '4.040.000'],
  ['1', '2.210.000', '2.050.000'],
  ['0.5', '1.150.000', '1.076.000'],
  ['',
   'Update harga LM Antam:07 September 2025 pukul 07.00Harga pembelian '
   'kembali:Rp1.989.000/grm',
   'Update harga LM Pegadaian:07 September 2025']],
 [['Satuan', 'Jual', 'Beli'],
  ['Gram', 'per Gram (Rp)', 'per Gram (Rp)'],
  ['0.1', '270.300', '186.500'],
  ['0.25', '611.800', '466.250'],
  ['0.5', '1.094.500', '932.500'],
  ['1', '2.009.000', '1.865.000'],
  ['2', '3.976.000', '3.730.000'],
  ['3', '5.953.500', '5.595.000'],
  ['4', '7.914.500', '7.460.000'],
  ['5', '9.787.000', '9.325.000'],
  ['10', '19.431.000', '18.650.000'],
  ['25', '48.459.000', '46.625.000'],
  ['50', '96.650.000', '93.250.000'],
  ['100', '192.321.000', '186.500.000']],
 [['Kurs', 'Beli', 'Jual'],
  ['AUD', '10.6565', '10.7686'],
  ['CAD', '11.8428', '11.9636'],
  ['CHF', '20.2879', '20.502'],
  ['DKK', '2.5481', '2.5739'],
  ['EUR', '19.0138', '19.2082'],
  ['GBP', '21.836', '22.0621'],
  ['HKD', '2.0938', '2.1149'],
  ['JPY', '10.9854', '11.0988'],
  ['MYR', '3.8615', '3.9049'],
  ['NZD', '9.5714', '9.6693'],
  ['SAR', '4.3552', '4.3992'],
  ['SEK', '1.7282', '1.7471'],
  ['SGD', '12.673', '12.8054'],
  ['THB', '50407', '50976'],
  ['USD', '16.3419', '16.5061']],
 [['Kurs', 'Beli', 'Jual'],
  ['AUD', '10726', '10766'],
  ['CAD', '11881', '11924'],
  ['CHF', '20390', '20461'],
  ['DKK', '2532', '2600'],
  ['EUR', '19118', '19182'],
  ['GBP', '22035', '22110'],
  ['HKD', '2099.56', '2112.22'],
  ['JPY', '110.77', '111.17'],
  ['MYR', '3877', '3900'],
  ['NZD', '9643', '9681'],
  ['SAR', '4366', '4390'],
  ['SEK', '1717', '1769'],
  ['SGD', '12724', '12770'],
  ['THB', '505.9', '510.76'],
  ['USD', '16435', '16465']],
 [['Kurs', 'Beli', 'Jual'],
  ['AUD', '10.7083', '10.8113'],
  ['CAD', '11.8235', '11.9077'],
  ['CHF', '20.4757', '20.6446'],
  ['DKK', '2.5498', '2.6016'],
  ['EUR', '19.1657', '19.295'],
  ['GBP', '22.0862', '22.2508'],
  ['HKD', '2.0951', '2.1142'],
  ['JPY', '11069', '11196'],
  ['MYR', '3.8629', '3.905'],
  ['NZD', '9.6244', '9.7176'],
  ['SAR', '4.3581', '4.3889'],
  ['SEK', '1.7189', '1.7743'],
  ['SGD', '12.724', '12.8201'],
  ['THB', '50781', '51525'],
  ['USD', '16.36', '16.46']],
 ['Emas 1 Gram', 'History', 'Trend', 'Perak 1 Gram', 'Pluang'],
 ['Tentang Kami', 'Widget', 'Privacy Policy'],
 ['Emas 1 Gram', 'History', 'Trend', 'Perak 1 Gram', 'Pluang'],
 ['Tentang Kami', 'Widget', 'Privacy Policy'])
([['IDR/gRp1.888.739+Rp0 (+0.00%)IDR/ozRp58.882.261+Rp0 (+0.00%)',
   'USD/g$115.32+$1.22 (+1.06%)USD/oz$3586.76+$38.02 (+1.06%)',
   'KursRp16.417+Rp0 (+0.00%)']],
 ['Emas 1 Gram', 'History', 'Trend', 'Perak 1 Gram', 'Pluang'],
 ['Tentang Kami', 'Widget', 'Privacy Policy'],
 ['Emas 1 Gram', 'History', 'Trend', 'Perak 1 Gram', 'Pluang'],
 ['Tentang Kami', 'Widget', 'Privacy Policy'])
```

## iloads

`iloads(data, syntax='yaml')`

Mengubah string data hasil dari idumps menjadi variabel.  
String data adalah berupa syntax YAML.  
  
```python  
data = {  
    'a': 123,  
    't': ['disini', 'senang', 'disana', 'senang'],  
    'l': (12, 23, [12, 42]),  
}  
s = idumps(data)  
print(iloads(s))  
```

Output:
```py
{'a': 123, 'l': (12, 23, [12, 42]), 't': ['disini', 'senang', 'disana', 'senang']}
```

## int_to_bin

`int_to_bin(n)`

Fungsi ini sama seperti fungsi bin().  
fungsi ini dibuat hanya untuk keperluan pembuatan module semata.  
  
```python  
print(int_to_bin(7777))  
```

Output:
```py
0b1111001100001
```

## int_to_hex

`int_to_hex(n)`

Fungsi ini sama seperti fungsi hex().  
fungsi ini dibuat hanya untuk keperluan pembuatan module semata.  
  
```python  
print(int_to_hex(7777))  
```

Output:
```py
0x1e61
```

## int_to_oct

`int_to_oct(n)`

Fungsi ini sama seperti fungsi oct().  
fungsi ini dibuat hanya untuk keperluan pembuatan module semata.  
  
```python  
print(int_to_oct(7777))  
```

Output:
```py
0o17141
```

## is_valid_url

`is_valid_url(path)`

Mengecek apakah path merupakan URL yang valid atau tidak.  
Cara ini merupakan cara yang paling efektif.  
  
```python  
print(is_valid_url("https://chat.openai.com/?model=text-davinci-002-render-sha"))  
print(is_valid_url("https://chat.openai.com/?model/=text-dav/inci-002-render-sha"))  
```

Output:
```py
True
True
```

## iopen

`iopen(path, data=None, regex=None, css_select=None, xpath=None, file_append=False)`

Membaca atau Tulis pada path yang bisa merupakan FILE maupun URL.  
  
Baca File :  
- Membaca seluruh file.  
- Jika berhasil content dapat diparse dengan regex.  
- Apabila File berupa html, dapat diparse dengan css atau xpath.  
  
Tulis File :  
- Menulis pada file.  
- Jika file tidak ada maka akan dibuat.  
- Jika file memiliki content maka akan di overwrite.  
  
Membaca URL :  
- Mengakses URL dan mengembalikan isi html nya berupa teks.  
- Content dapat diparse dengan regex, css atau xpath.  
  
Tulis URL :  
- Mengirimkan data dengan metode POST ke url.  
- Jika berhasil dan response memiliki content, maka dapat diparse  
  dengan regex, css atau xpath.  
  
  
```python  
# FILE  
print(iopen("__iopen.txt", "mana aja"))  
print(iopen("__iopen.txt", regex="([a-zA-Z])"))  
# URL  
print(iopen("https://www.google.com/", css_select="a"))  
print(iopen("https://www.google.com/", dict(coba="dulu"), xpath="//a"))  
```

Output:
```py
8
['m', 'a', 'n', 'a', 'a', 'j', 'a']
False
False
```

## iprint

`iprint(*args, color=None, sort_dicts=False, **kwargs)`

Improve print function dengan menambahkan color dan pretty print  
Color menggunakan colorama Fore + Back + Style  
  
```python  
import colorama  
iprint(  
    'yang ini',  
    {'12':12,'sdsd':{'12':21,'as':[88]}},  
    color=colorama.Fore.BLUE + colorama.Style.BRIGHT  
)  
```

Output:
```py
[34m[1myang ini[0m [34m[1m{'12': 12, 'sdsd': {'12': 21, 'as': [88]}}[0m
```

## is_raw_string

`is_raw_string(s)`

## ireplace

`ireplace(string: str, replacements: dict, flags=re.IGNORECASE|re.MULTILINE|re.DOTALL)`

STRing TRanslate mengubah string menggunakan kamus dari dict.  
Replacement dapat berupa text biasa ataupun regex pattern.  
Apabila replacement berupa regex, gunakan raw string `r"..."`  
Untuk regex capturing gunakan `(...)`, dan untuk mengaksesnya  
gunakan `\1`, `\2`, .., dst.  
  
```python  
text = 'aku ini mau ke sini'  
replacements = {  
    "sini": "situ",  
    r"(ini)": r"itu dan \1",  
}  
print(ireplace(text, replacements))  
```

Output:
```py
aku itu dan ini mau ke situ
```

## is_file_exist

`is_file_exist(path)`

## is_html

`is_html(text)`

## iscandir

`iscandir(folder_name='.', glob_pattern='*', recursive=True, scan_file=True, scan_folder=True)`

Mempermudah scandir untuk mengumpulkan folder dan file.  
  
```python  
print(iscandir())  
print(list(iscandir("./", recursive=False, scan_file=False)))  
```

Output:
```py
<generator object iscandir at 0x7eed670f40>
[PosixPath('.git'), PosixPath('.vscode'), PosixPath('pypipr'), PosixPath('__pycache__'), PosixPath('dist')]
```

## isplit

`isplit(text, separator='', include_separator=False)`

Memecah text menjadi list berdasarkan separator.  
  
```python  
t = '/ini/contoh/path/'  
print(isplit(t, separator='/'))  
```

Output:
```py
['', 'ini', 'contoh', 'path', '']
```

## ivars

`ivars(obj, skip_underscore=True)`

Membuat dictionary berdasarkan kategori untuk setiap  
member dari object.  
  
```python  
iprint(ivars(__import__('pypipr')))  
```

Output:
```py
{'function': {'avg': <function avg at 0x7efb5b7a60>,
              'get_filemtime': <function get_filemtime at 0x7ef3171440>,
              'print_colorize': <function print_colorize at 0x7ef3171620>,
              'print_log': <function print_log at 0x7ef31714e0>,
              'console_run': <function console_run at 0x7ef3171580>,
              'auto_reload': <function auto_reload at 0x7efaab87c0>,
              'basename': <function basename at 0x7ef31716c0>,
              'chr_to_int': <function chr_to_int at 0x7ef3171c60>,
              'int_to_chr': <function int_to_chr at 0x7ef3171d00>,
              'irange': <function irange at 0x7ef3171f80>,
              'batchmaker': <function batchmaker at 0x7ef31719e0>,
              'calculate': <function calculate at 0x7ef3171a80>,
              'batch_calculate': <function batch_calculate at 0x7ef3171760>,
              'bin_to_int': <function bin_to_int at 0x7ef3171940>,
              'is_empty': <function is_empty at 0x7ef3172840>,
              'exit_if_empty': <function exit_if_empty at 0x7ef3172660>,
              'input_char': <function input_char at 0x7ef31727a0>,
              'choices': <function choices at 0x7ef3172ac0>,
              'chunk_array': <function chunk_array at 0x7ef3172b60>,
              'create_folder': <function create_folder at 0x7ef3172c00>,
              'datetime_from_string': <function datetime_from_string at 0x7ef3172ca0>,
              'datetime_now': <function datetime_now at 0x7ef3172d40>,
              'dict_first': <function dict_first at 0x7ef3148f40>,
              'traceback_filename': <function traceback_filename at 0x7ef3149120>,
              'dirname': <function dirname at 0x7ef3148fe0>,
              'dirpath': <function dirpath at 0x7ef31491c0>,
              'django_clear_migrations': <function django_clear_migrations at 0x7ef3149260>,
              'django_runserver': <function django_runserver at 0x7ef3149580>,
              'is_iterable': <function is_iterable at 0x7ef3149940>,
              'to_str': <function to_str at 0x7ef31499e0>,
              'filter_empty': <function filter_empty at 0x7ef3149800>,
              'get_by_index': <function get_by_index at 0x7ef3149080>,
              'get_class_method': <function get_class_method at 0x7ef3149a80>,
              'get_filesize': <function get_filesize at 0x7ef3149bc0>,
              'github_init': <function github_init at 0x7ef3149c60>,
              'github_pull': <function github_pull at 0x7ef3149d00>,
              'github_push': <function github_push at 0x7ef3149e40>,
              'github_user': <function github_user at 0x7ef3149ee0>,
              'hex_to_int': <function hex_to_int at 0x7ef3149f80>,
              'iargv': <function iargv at 0x7ef314a020>,
              'idir': <function idir at 0x7ef314a0c0>,
              'idumps_html': <function idumps_html at 0x7ef2fe1c60>,
              'idumps': <function idumps at 0x7ef314a160>,
              'int_to_int': <function int_to_int at 0x7ef2fe20c0>,
              'ienumerate': <function ienumerate at 0x7ef314a200>,
              'ienv': <function ienv at 0x7ef2fe1f80>,
              'iexec': <function iexec at 0x7ef2fe2160>,
              'iinput': <function iinput at 0x7ef2fe2200>,
              'ijoin': <function ijoin at 0x7ef2fe22a0>,
              'iloads_html': <function iloads_html at 0x7ef2fe25c0>,
              'iloads': <function iloads at 0x7ef3149b20>,
              'int_to_bin': <function int_to_bin at 0x7efc035260>,
              'int_to_hex': <function int_to_hex at 0x7ef2fe2340>,
              'int_to_oct': <function int_to_oct at 0x7ef2fe2660>,
              'is_valid_url': <function is_valid_url at 0x7ef3046480>,
              'iopen': <function iopen at 0x7ef2fe27a0>,
              'iprint': <function iprint at 0x7ef30465c0>,
              'is_raw_string': <function is_raw_string at 0x7ef11ac180>,
              'ireplace': <function ireplace at 0x7ef3046520>,
              'is_file_exist': <function is_file_exist at 0x7ef11ac0e0>,
              'is_html': <function is_html at 0x7ef11ac220>,
              'iscandir': <function iscandir at 0x7ef11ac2c0>,
              'isplit': <function isplit at 0x7ef11ac360>,
              'ivars': <function ivars at 0x7ef11ac400>,
              'log': <function log at 0x7ef11ac4a0>,
              'no_indent': <function no_indent at 0x7ef11ac540>,
              'oct_to_int': <function oct_to_int at 0x7ef11ac5e0>,
              'password_generator': <function password_generator at 0x7ef11ac680>,
              'path_to_module': <function path_to_module at 0x7ef11ac720>,
              'pip_freeze_without_version': <function pip_freeze_without_version at 0x7ef11ac7c0>,
              'pip_update_pypipr': <function pip_update_pypipr at 0x7ef11ac860>,
              'poetry_publish': <function poetry_publish at 0x7ef11ac900>,
              'poetry_shell': <function poetry_shell at 0x7ef11ac9a0>,
              'poetry_update_version': <function poetry_update_version at 0x7ef11acae0>,
              'print_dir': <function print_dir at 0x7ef11acc20>,
              'print_to_last_line': <function print_to_last_line at 0x7ef11accc0>,
              'random_bool': <function random_bool at 0x7ef11acd60>,
              'repath': <function repath at 0x7ef11acea0>,
              'restart': <function restart at 0x7ef11acf40>,
              'set_timeout': <function set_timeout at 0x7ef11acfe0>,
              'sets_ordered': <function sets_ordered at 0x7ef11ad080>,
              'sqlite_backup': <function sqlite_backup at 0x7ef11ad120>,
              'sqlite_delete_table': <function sqlite_delete_table at 0x7ef11ad1c0>,
              'sqlite_get_all_tables': <function sqlite_get_all_tables at 0x7ef11ad260>,
              'sqlite_get_data_table': <function sqlite_get_data_table at 0x7ef11ad300>,
              'str_cmp': <function str_cmp at 0x7ef11adbc0>,
              'text_colorize': <function text_colorize at 0x7ef11adc60>,
              'tiles': <function tiles at 0x7ef11add00>,
              'traceback_framename': <function traceback_framename at 0x7ef11adda0>},
 'class': {'ComparePerformance': <class 'pypipr.ComparePerformance.ComparePerformance'>,
           'PintUregQuantity': <class 'pint.Quantity'>,
           'RunParallel': <class 'pypipr.RunParallel.RunParallel'>},
 'variable': {'LINUX': True,
              'PintUreg': <pint.registry.UnitRegistry object at 0x7efb5e81d0>,
              'WINDOWS': False},
 'module': {'asyncio': <module 'asyncio' from '/data/data/com.termux/files/usr/lib/python3.12/asyncio/__init__.py'>,
            'colorama': <module 'colorama' from '/data/data/com.termux/files/usr/lib/python3.12/site-packages/colorama/__init__.py'>,
            'csv': <module 'csv' from '/data/data/com.termux/files/usr/lib/python3.12/csv.py'>,
            'datetime': <module 'datetime' from '/data/data/com.termux/files/usr/lib/python3.12/datetime.py'>,
            'functools': <module 'functools' from '/data/data/com.termux/files/usr/lib/python3.12/functools.py'>,
            'inspect': <module 'inspect' from '/data/data/com.termux/files/usr/lib/python3.12/inspect.py'>,
            'io': <module 'io' (frozen)>,
            'json': <module 'json' from '/data/data/com.termux/files/usr/lib/python3.12/json/__init__.py'>,
            'lxml': <module 'lxml' from '/data/data/com.termux/files/usr/lib/python3.12/site-packages/lxml/__init__.py'>,
            'math': <module 'math' from '/data/data/com.termux/files/usr/lib/python3.12/lib-dynload/math.cpython-312.so'>,
            'multiprocessing': <module 'multiprocessing' from '/data/data/com.termux/files/usr/lib/python3.12/multiprocessing/__init__.py'>,
            'operator': <module 'operator' from '/data/data/com.termux/files/usr/lib/python3.12/operator.py'>,
            'os': <module 'os' (frozen)>,
            'pathlib': <module 'pathlib' from '/data/data/com.termux/files/usr/lib/python3.12/pathlib.py'>,
            'pint': <module 'pint' from '/data/data/com.termux/files/usr/lib/python3.12/site-packages/pint/__init__.py'>,
            'pprint': <module 'pprint' from '/data/data/com.termux/files/usr/lib/python3.12/pprint.py'>,
            'queue': <module 'queue' from '/data/data/com.termux/files/usr/lib/python3.12/queue.py'>,
            'random': <module 'random' from '/data/data/com.termux/files/usr/lib/python3.12/random.py'>,
            're': <module 're' from '/data/data/com.termux/files/usr/lib/python3.12/re/__init__.py'>,
            'requests': <module 'requests' from '/data/data/com.termux/files/usr/lib/python3.12/site-packages/requests/__init__.py'>,
            'string': <module 'string' from '/data/data/com.termux/files/usr/lib/python3.12/string.py'>,
            'subprocess': <module 'subprocess' from '/data/data/com.termux/files/usr/lib/python3.12/subprocess.py'>,
            'sys': <module 'sys' (built-in)>,
            'textwrap': <module 'textwrap' from '/data/data/com.termux/files/usr/lib/python3.12/textwrap.py'>,
            'threading': <module 'threading' from '/data/data/com.termux/files/usr/lib/python3.12/threading.py'>,
            'time': <module 'time' (built-in)>,
            'traceback': <module 'traceback' from '/data/data/com.termux/files/usr/lib/python3.12/traceback.py'>,
            'tzdata': <module 'tzdata' from '/data/data/com.termux/files/usr/lib/python3.12/site-packages/tzdata/__init__.py'>,
            'uuid': <module 'uuid' from '/data/data/com.termux/files/usr/lib/python3.12/uuid.py'>,
            'webbrowser': <module 'webbrowser' from '/data/data/com.termux/files/usr/lib/python3.12/webbrowser.py'>,
            'yaml': <module 'yaml' from '/data/data/com.termux/files/usr/lib/python3.12/site-packages/yaml/__init__.py'>,
            'zoneinfo': <module 'zoneinfo' from '/data/data/com.termux/files/usr/lib/python3.12/zoneinfo/__init__.py'>}}
```

## log

`log(text=None)`

Decorator untuk mempermudah pembuatan log karena tidak perlu mengubah  
fungsi yg sudah ada.  
Melakukan print ke console untuk menginformasikan proses yg sedang  
berjalan didalam program.  
  
```py  
@log  
def some_function():  
    pass  
  
@log()  
def some_function_again():  
    pass  
  
@log("Calling some function")  
def some_function_more():  
    pass  
  
some_function()  
some_function_again()  
some_function_more()  
```

## no_indent

`no_indent(teks)`

## oct_to_int

`oct_to_int(n)`

Fungsi ini berguna untuk mengubah angka octal   
menjadi angka integer.  
  
```python  
print(oct_to_int(oct(244)))  
```

Output:
```py
244
```

## password_generator

`password_generator(length=8, characters='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')`

Membuat pssword secara acak  
  
```python  
print(password_generator())  
```

Output:
```py
jxX^Za2H
```

## path_to_module

`path_to_module(path, indeks=0)`

Mengubah absolute path file menjadi path modul relatif terhadap cwd (current working directory),  
dengan opsi untuk memangkas bagian akhir path berdasarkan indeks.  
  
Parameter:  
    abs_path (str): Path absolut menuju file.  
    indeks (int):  
        - 0 => hasil lengkap hingga file (tanpa ekstensi),  
        - -1 => tanpa nama file, hanya foldernya,  
        - -2 => dua folder di atasnya, dst.  
  
Returns:  
    str: Path bergaya modul Python (dipisah dengan ".")

## pip_freeze_without_version

`pip_freeze_without_version(filename=None)`

Memberikan list dari dependencies yang terinstall tanpa version.  
Bertujuan untuk menggunakan Batteries Included Python.  
  
```py  
print(pip_freeze_without_version())  
```

## pip_update_pypipr

`pip_update_pypipr()`

## poetry_publish

`poetry_publish(token=None)`

Publish project to pypi,org  
  
```py  
poetry_publish()  
```

## poetry_shell

`poetry_shell()`

Masuk ke virtual environment poetry  
  
```py  
poetry_shell()  
```

## poetry_update_version

`poetry_update_version(mayor=False, minor=False, patch=False)`

Update versi pada pyproject.toml menggunakan poetry  
  
```py  
poetry_update_version()  
```

## print_dir

`print_dir(var, colorize=True)`

Print property dan method yang tersedia pada variabel  
  
```python  
import pathlib  
p = pathlib.Path("https://www.google.com/")  
print_dir(p, colorize=False)  
```

Output:
```py
             __bytes__ : b'https:/www.google.com'
             __class__ : .
               __dir__ : ['__module__', '__doc__', '__slots__', 'stat', 'lstat', 'exists', 'is_dir', 'is_file', 'is_mount', 'is_symlink', 'is_junction', 'is_block_device', 'is_char_device', 'is_fifo', 'is_socket', 'samefile', 'open', 'read_bytes', 'read_text', 'write_bytes', 'write_text', 'iterdir', '_scandir', '_make_child_relpath', 'glob', 'rglob', 'walk', '__init__', '__new__', '__enter__', '__exit__', 'cwd', 'home', 'absolute', 'resolve', 'owner', 'group', 'readlink', 'touch', 'mkdir', 'chmod', 'lchmod', 'unlink', 'rmdir', 'rename', 'replace', 'symlink_to', 'hardlink_to', 'expanduser', '_flavour', '__reduce__', 'with_segments', '_parse_path', '_load_parts', '_from_parsed_parts', '_format_parsed_parts', '__str__', '__fspath__', 'as_posix', '__bytes__', '__repr__', 'as_uri', '_str_normcase', '_parts_normcase', '_lines', '__eq__', '__hash__', '__lt__', '__le__', '__gt__', '__ge__', 'drive', 'root', '_tail', 'anchor', 'name', 'suffix', 'suffixes', 'stem', 'with_name', 'with_stem', 'with_suffix', 'relative_to', 'is_relative_to', 'parts', 'joinpath', '__truediv__', '__rtruediv__', 'parent', 'parents', 'is_absolute', 'is_reserved', 'match', '_drv', '_hash', '_lines_cached', '_parts_normcase_cached', '_raw_paths', '_root', '_str', '_str_normcase_cached', '_tail_cached', '__getattribute__', '__setattr__', '__delattr__', '__ne__', '__reduce_ex__', '__getstate__', '__subclasshook__', '__init_subclass__', '__format__', '__sizeof__', '__dir__', '__class__']
               __doc__ : Path subclass for non-Windows systems.

    On a POSIX system, instantiating a Path should return this object.
    
             __enter__ : https:/www.google.com
            __fspath__ : https:/www.google.com
          __getstate__ : (None, {'_raw_paths': ['https://www.google.com/'], '_drv': '', '_root': '', '_tail_cached': ['https:', 'www.google.com'], '_str': 'https:/www.google.com'})
              __hash__ : -3749585103093151224
              __init__ : None
     __init_subclass__ : None
            __module__ : pathlib
            __reduce__ : (<class 'pathlib.PosixPath'>, ('https:', 'www.google.com'))
              __repr__ : PosixPath('https:/www.google.com')
            __sizeof__ : 88
             __slots__ : ()
               __str__ : https:/www.google.com
      __subclasshook__ : NotImplemented
                  _drv : 
              _flavour : <module 'posixpath' (frozen)>
                 _hash : -3749585103093151224
                _lines : https:
www.google.com
         _lines_cached : https:
www.google.com
           _load_parts : None
       _parts_normcase : ['https:', 'www.google.com']
_parts_normcase_cached : ['https:', 'www.google.com']
            _raw_paths : []
                 _root : 
                  _str : https:/www.google.com
         _str_normcase : https:/www.google.com
  _str_normcase_cached : https:/www.google.com
                 _tail : []
          _tail_cached : []
              absolute : /data/data/com.termux/files/home/r/p
                anchor : 
              as_posix : https:/www.google.com
                   cwd : /data/data/com.termux/files/home/r/p
                 drive : 
                exists : False
            expanduser : https:/www.google.com
                  home : /data/data/com.termux/files/home
           is_absolute : False
       is_block_device : False
        is_char_device : False
                is_dir : False
               is_fifo : False
               is_file : False
           is_junction : False
              is_mount : False
           is_reserved : False
             is_socket : False
            is_symlink : False
               iterdir : <generator object Path.iterdir at 0x7eed68d490>
              joinpath : .
                  name : 
                parent : https:/www.google.com
               parents : <PosixPath.parents>
                 parts : ()
               resolve : /data/data/com.termux/files/home/r/p/https:/www.google.com
                  root : 
                  stem : 
                suffix : 
              suffixes : []
                  walk : <generator object Path.walk at 0x7eed625bc0>
         with_segments : .
```

## print_to_last_line

`print_to_last_line(text: str, latest=1, clear=True)`

Melakukan print ke konsol tetapi akan menimpa baris terakhir.  
Berguna untuk memberikan progress secara interaktif.  
  
```python  
for i in range(5):  
    print(str(i) * 10)  
print_to_last_line(f" === last ===")  
```

Output:
```py
0000000000
1111111111
2222222222
3333333333
4444444444
[1A[K === last ===
```

## random_bool

`random_bool()`

Menghasilkan nilai random True atau False.  
Fungsi ini merupakan fungsi tercepat untuk mendapatkan random bool.  
Fungsi ini sangat cepat, tetapi pemanggilan fungsi ini membutuhkan  
overhead yg besar.  
  
```python  
print(random_bool())  
```

Output:
```py
False
```

## repath

`repath(path, folder_name=None, prepand_folder=None, append_folder=None, file_name=None, prepand_filename=None, append_filename=None, extension=None, prepand_extension=None, append_extension=None)`

## restart

`restart(*argv)`

Mengulang program dari awal seperti memulai awal.  
  
Bisa ditambahkan dengan argumen tambahan  
  
```py  
restart("--stdio")  
```

## set_timeout

`set_timeout(interval, func, args=None, kwargs=None)`

Menjalankan fungsi ketika sudah sekian detik.  
Apabila timeout masih berjalan tapi kode sudah selesai dieksekusi semua, maka  
program tidak akan berhenti sampai timeout selesai, kemudian fungsi dijalankan,  
kemudian program dihentikan.  
  
```python  
set_timeout(3, lambda: print("Timeout 3"))  
x = set_timeout(7, print, args=["Timeout 7"])  
print(x)  
print("menghentikan timeout 7")  
x.cancel()  
```

Output:
```py
<Timer(Thread-2, started 545122680048)>
menghentikan timeout 7
```

## sets_ordered

`sets_ordered(iterator)`

Hanya mengambil nilai unik dari suatu list  
  
```python  
array = [2, 3, 12, 3, 3, 42, 42, 1, 43, 2, 42, 41, 4, 24, 32, 42, 3, 12, 32, 42, 42]  
print(sets_ordered(array))  
print(list(sets_ordered(array)))  
```

Output:
```py
<generator object sets_ordered at 0x7eed68d7d0>
[2, 3, 12, 42, 1, 43, 41, 4, 24, 32]
```

## sqlite_backup

`sqlite_backup(db)`

## sqlite_delete_table

`sqlite_delete_table(filename, tablename)`

Perintah sederhana untuk menghapus tabel  
dari database SQLite.

## sqlite_get_all_tables

`sqlite_get_all_tables(filename)`

Perintah SQLite untuk menampilkan seluruh tabel  
yang ada pada database.  
Hanya akan mengembalikan kolom nama tabel saja.

## sqlite_get_data_table

`sqlite_get_data_table(filename, tablename)`

Perintah SQLite untuk menampilkan seluruh data  
pada tabel database

## str_cmp

`str_cmp(t1, t2)`

Membandingakan string secara incase-sensitive menggunakan lower().  
Lebih cepat dibandingkan upper(), casefold(), re.fullmatch(), len().  
perbandingan ini sangat cepat, tetapi pemanggilan fungsi ini membutuhkan  
overhead yg besar.  
  
```python  
print(str_cmp('teks1', 'Teks1'))  
```

Output:
```py
True
```

## text_colorize

`text_colorize(text, color='\x1b[32m', bright='\x1b[1m', color_end='\x1b[0m')`

return text dengan warna untuk menunjukan text penting  
  
```py  
text_colorize("Print some text")  
text_colorize("Print some text", color=colorama.Fore.RED)  
```

## tiles

`tiles(tile_x=None, tile_y=None, area_x=None, area_y=None, gap_x=None, gap_y=None)`

## traceback_framename

`traceback_framename(stack_level=-3)`

Mendapatkan frame name dimana fungsi yg memanggil  
fungsi dimana fungsi ini diletakan ini dipanggil.  
  
```py  
print(traceback_framename())  
```

# CLASS

## ComparePerformance

`ComparePerformance()`

Menjalankan seluruh method dalam class,  
Kemudian membandingkan waktu yg diperlukan.  
Nilai 100 berarti yang tercepat.  
  
```python  
class ExampleComparePerformance(ComparePerformance):  
    # number = 1  
    z = 10  
  
    def a(self):  
        return (x for x in range(self.z))  
  
    def b(self):  
        return tuple(x for x in range(self.z))  
  
    def c(self):  
        return [x for x in range(self.z)]  
  
    def d(self):  
        return list(x for x in range(self.z))  
  
pprint.pprint(ExampleComparePerformance().compare_result(), depth=100)  
print(ExampleComparePerformance().compare_performance())  
print(ExampleComparePerformance().compare_performance())  
print(ExampleComparePerformance().compare_performance())  
print(ExampleComparePerformance().compare_performance())  
print(ExampleComparePerformance().compare_performance())  
```

Output:
```py
{'a': <generator object ExampleComparePerformance.a.<locals>.<genexpr> at 0x7eed634ac0>,
 'b': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
 'c': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
 'd': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}
{'a': 141, 'b': 142, 'c': 100, 'd': 139}
{'a': 129, 'b': 165, 'c': 100, 'd': 166}
{'a': 121, 'b': 167, 'c': 99, 'd': 170}
{'a': 126, 'b': 170, 'c': 100, 'd': 176}
{'a': 118, 'b': 161, 'c': 100, 'd': 164}
```

## PintUregQuantity

`PintUregQuantity(value, units=None)`

## RunParallel

`RunParallel()`

Menjalankan program secara bersamaan.  
  
- `class RunParallel` didesain hanya untuk pemrosesan data saja.  
- Penggunaannya `class RunParallel` dengan cara membuat instance  
  sub class beserta data yg akan diproses, kemudian panggil fungsi  
  yg dipilih `run_asyncio / run_multi_threading / run_multi_processing`,  
  kemudian dapatkan hasilnya.  
- `class RunParallel` tidak didesain untuk menyimpan data, karena  
  setiap module terutama module `multiprocessing` tidak dapat mengakses  
  data kelas dari proses yg berbeda.  
- Semua methods akan dijalankan secara paralel kecuali method dengan  
  nama yg diawali underscore `_`  
- Method untuk multithreading/multiprocessing harus memiliki 2  
  parameter, yaitu: `result: dict` dan `q: queue.Queue`. Parameter  
  `result` digunakan untuk memberikan return value dari method, dan  
  Parameter `q` digunakan untuk mengirim data antar proses.  
- Method untuk asyncio harus menggunakan keyword `async def`, dan  
  untuk perpindahan antar kode menggunakan `await asyncio.sleep(0)`,  
  dan keyword `return` untuk memberikan return value.  
- Return Value berupa dictionary dengan key adalah nama function,  
  dan value adalah return value dari setiap fungsi  
- Menjalankan Multiprocessing harus berada dalam blok  
  `if __name__ == "__main__":` karena area global pada program akan  
  diproses lagi. Terutama pada sistem operasi windows.  
- `run_asyncio()` akan menjalankan kode dalam satu program, hanya  
  saja alur program dapat berpindah-pindah menggunkan  
  `await asyncio.sleep(0)`.  
- `run_multi_threading()` akan menjalankan program dalam satu CPU,  
  hanya saja dalam thread yang berbeda. Walaupun tidak benar-benar  
  berjalan secara bersamaan namun bisa meningkatkan kecepatan  
  penyelesaian program, dan dapat saling mengakses resource antar  
  program.  Akses resource antar program bisa secara langsung maupun  
  menggunakan parameter yang sudah disediakan yaitu `result: dict`  
  dan `q: queue.Queue`.  
- `run_multi_processing()` akan menjalankan program dengan beberapa  
  CPU. Program akan dibuatkan environment sendiri yang terpisah dari  
  program induk. Keuntungannya adalah program dapat benar-benar berjalan  
  bersamaan, namun tidak dapat saling mengakses resource secara langsung.  
  Akses resource menggunakan parameter yang sudah disediakan yaitu  
  `result: dict` dan `q: queue.Queue`.  
  
```py  
class ExampleRunParallel(RunParallel):  
    z = "ini"  
  
    def __init__(self) -> None:  
        self.pop = random.randint(0, 100)  
  
    def _set_property_here(self, v):  
        self.prop = v  
  
    def a(self, result: dict, q: queue.Queue):  
        result["z"] = self.z  
        result["pop"] = self.pop  
        result["a"] = "a"  
        q.put("from a 1")  
        q.put("from a 2")  
  
    def b(self, result: dict, q: queue.Queue):  
        result["z"] = self.z  
        result["pop"] = self.pop  
        result["b"] = "b"  
        result["q_get"] = q.get()  
  
    def c(self, result: dict, q: queue.Queue):  
        result["z"] = self.z  
        result["pop"] = self.pop  
        result["c"] = "c"  
        result["q_get"] = q.get()  
  
    async def d(self):  
        print("hello")  
        await asyncio.sleep(0)  
        print("hello")  
  
        result = {}  
        result["z"] = self.z  
        result["pop"] = self.pop  
        result["d"] = "d"  
        return result  
  
    async def e(self):  
        print("world")  
        await asyncio.sleep(0)  
        print("world")  
  
        result = {}  
        result["z"] = self.z  
        result["pop"] = self.pop  
        result["e"] = "e"  
        return result  
  
if __name__ == "__main__":  
    print(ExampleRunParallel().run_asyncio())  
    print(ExampleRunParallel().run_multi_threading())  
    print(ExampleRunParallel().run_multi_processing())  
```
