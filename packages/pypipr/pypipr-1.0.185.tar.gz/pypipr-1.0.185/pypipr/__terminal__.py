from pypipr import *


def input_parameter(o):
    try:
        return eval(o)
    except Exception:
        return o



def main(module="pypipr"):
    module = __import__(module)
    m = ivars(module)
    m = m["module"] | m["variable"] | m["class"] | m["function"]
    # m = m["variable"] | m["function"]
    m = [x for x in m]
    m.sort()

    a = iargv(1)
    p = "Masukan Nomor Urut atau Nama Fungsi : "
    m = choices(daftar=m, contains=a, prompt=p)

    f = getattr(module, m)

    if a != m:
        print_colorize(m)
        print(f.__doc__)


    if inspect.isclass(f):
        print_log("Class tidak dapat dijalankan.")
    elif inspect.ismodule(f):
        print_log("Module tidak dapat dijalankan.")
        main(f.__name__)
        return
    elif inspect.isfunction(f):
        s = inspect.signature(f)

        if not a:
            print(m, end="")
            print_colorize(s)

        k = {}
        for i, v in s.parameters.items():
            o = input(f"{i} [{v.default}] : ")
            if len(o):
                try:
                    k[i] = input_parameter(o)
                except Exception:
                    print_colorize(
                        "Input harus dalam syntax python.",
                        color=colorama.Fore.RED,
                    )

        f = f(**k)

    else:
        # variable
        pass

    iprint(f)


if __name__ == "__main__":
    main()
