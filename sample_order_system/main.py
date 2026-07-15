"""SampleOrderSystem 콘솔 앱 진입점."""

from mvc import Application

from .app.model import SampleOrderModel
from .app.view import SampleOrderView
from .app.controller import SampleOrderController


def main():
    app = Application(SampleOrderModel(), SampleOrderView(), SampleOrderController)
    app.run()


if __name__ == "__main__":
    main()
