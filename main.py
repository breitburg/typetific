from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QBrush, QPen, QColor, QFont
from PySide6.QtCore import Qt

from random import choice
from english_words import english_words_set
from time import time
from statistics import mean
from string import printable

printable_ords = set([ord(char) for char in printable])


class TypingWindow(QWidget):
    def __init__(self, parent=None):
        super(TypingWindow, self).__init__(parent=parent)

        self.config = {
            'error_color': QColor(255, 190, 190),
            'done_color': QColor(190, 255, 190),
            'secondary_color': QColor(215, 215, 215),
            'background_color': QColor(255, 255, 255),
            'primary_color': QColor(34, 34, 34),
            'line_padding': 10, 'font_factor': 7
        }

        self.reset()
        self.setupWindow()

    def paintEvent(self, event):
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.setFont(QFont('Menlo', event.rect().height() / self.config['font_factor']))

        self.isEnd = self.pointer >= len(self.text)

        # Line
        lineX = event.rect().width() / 6
        letterSize = self.painter.fontMetrics()
        textY = event.rect().height() / 2 + letterSize.height() / 4
        lineColor = self.config['done_color'] if self.isEnd else (
            self.config['error_color'] if len(self.events) > 0 and not self.events[-1][
                'correct'] else self.config['secondary_color'])
        lineWidth = letterSize.maxWidth() + self.config['line_padding']
        self.painter.setPen(QPen(lineColor, 1, Qt.SolidLine))
        self.painter.setBrush(QBrush(lineColor, Qt.SolidPattern))
        self.painter.drawRect(lineX, 0, lineWidth, event.rect().height())

        # Primary Text
        if not self.isEnd:
            self.painter.setPen(self.config['primary_color'])
            self.painter.drawText(lineX + self.config['line_padding'] / 2, textY, self.text[self.pointer])
            self.painter.drawText(lineX + lineWidth + self.config['line_padding'] / 2, textY,
                                  self.text[self.pointer + 1:])
        else:
            speed = round(60 / mean(
                [event['time'] - self.events[self.events.index(event) - 1]['time'] for event in self.events[1:]]))
            typos = len([event for event in self.events if not event['correct']])

            print('ff')
            self.painter.setPen(self.config['background_color'])
            self.painter.drawText(lineX + lineWidth + self.config['line_padding'], textY,
                                  'S: {}, E: {}'.format(speed, typos))

        # Typed Text
        typedTextSize = self.painter.fontMetrics().size(Qt.TextSingleLine, self.text[:self.pointer])
        self.painter.setPen(self.config['secondary_color'])
        self.painter.drawText(lineX - typedTextSize.width() - self.config['line_padding'] / 2, textY,
                              self.text[:self.pointer])

        self.painter.end()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Return:
            self.reset()
            return

        if event.key() not in printable_ords or self.isEnd:
            return

        isCorrect = event.text() == self.text[self.pointer]
        self.events.append({
            'key': event.text(),
            'pointer': self.pointer,
            'correct': isCorrect,
            'time': time()
        })

        self.pointer += 1
        self.repaint()

    def reset(self) -> None:
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
