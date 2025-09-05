import sortingview.views as vv
import kachery as ka


def main():
    ka.use_sandbox()
    view = example_image()

    url = view.url(label="Image example")
    print(url)


def example_image():
    view = vv.Image(image_path="./figurl192.png")
    return view


if __name__ == "__main__":
    main()
