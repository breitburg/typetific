from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QBrush, QPen, QColor, QFont
from PySide6.QtCore import Qt

from random import choice
from english_words import english_words_set
from time import time
from string import printable
from statistics import mean


class TypingWindow(QWidget):
    def __init__(self, parent=None):
        super(TypingWindow, self).__init__(parent=parent)

        '''
        self.config = {
            'error_color': QColor(130, 0, 0),
            'secondary_color': QColor(40, 40, 40),
            'background_color': QColor(0, 0, 0),
            'primary_color': QColor(255, 255, 255),
            'line_padding': 10, 'font_factor': 8
        }
        '''

        self.config = {
            'error_color': QColor(255, 190, 190),
            'secondary_color': QColor(215, 215, 215),
            'background_color': QColor(255, 255, 255),
            'primary_color': QColor(34, 34, 34),
            'line_padding': 10, 'font_factor': 8
        }

        self.events = []
        self.reset()
        self.setupWindow()

    def paintEvent(self, event):
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.setFont(QFont('Menlo', event.rect().height() / self.config['font_factor']))

        lineX = event.rect().width() / 6
        letterSize = self.painter.fontMetrics().size(Qt.TextSingleLine, self.text[self.pointer])

        # Line
        lineColor = self.config['error_color'] if (
            not self.events[-1]['isCorrect'] if len(self.events) > 0 else False) else self.config['secondary_color']
        self.painter.setPen(QPen(lineColor, 1, Qt.SolidLine))
        self.painter.setBrush(QBrush(lineColor, Qt.SolidPattern))
        self.painter.drawRect(lineX, 0, letterSize.width() + self.config['line_padding'], event.rect().height())

        # Primary Text
        textY = event.rect().height() / 2 + letterSize.height() / 4
        self.painter.setPen(self.config['primary_color'])
        self.painter.drawText(lineX + self.config['line_padding'] / 2, textY,
                              self.text[self.pointer])
        self.painter.drawText(lineX + letterSize.width() + self.config['line_padding'], textY,
                              self.text[self.pointer + 1:])

        # Typed Text
        typedText = self.painter.fontMetrics().size(Qt.TextSingleLine, self.text[:self.pointer]).width()
        self.painter.setPen(self.config.get('secondary_color'))
        self.painter.drawText(lineX - typedText - self.config.get('line_padding') / 2, textY,
                              self.text[:self.pointer])

        self.painter.end()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Return or self.pointer + 1 >= len(self.text):
            self.reset()
            return

        if event.text() not in printable:
            return

        isCorrect = event.text() == self.text[self.pointer]
        self.events.append({
            'key': event.text(),
            'pointer': self.pointer,
            'isCorrect': isCorrect,
            'time': time()
        })

        self.pointer += 1
        self.repaint()

    def reset(self) -> None:
        if len(self.events) > 0:
            speed = round(60 / mean(
                [event['time'] - self.events[self.events.index(event) - 1]['time'] for event in self.events[1:]]))
            print('speed: {} char/min, typos: {}'.format(speed, len(
                [event for event in self.events if not event['isCorrect']])))

        self.events = []
        self.text = ' '.join([choice(list(english_words_set)).lower() for _ in range(10)])
        self.pointer = 0

        self.repaint()

    def setupWindow(self) -> None:
        self.setWindowTitle('Type')
        self.setMinimumSize(1100, 620)
        self.setStyleSheet('background: {}; color: {};'.format(self.config['background_color'].name(),
                                                               self.config['primary_color'].name()))


if __name__ == '__main__':
    app = QApplication()

    window = TypingWindow()
    window.show()

    app.exec_()
