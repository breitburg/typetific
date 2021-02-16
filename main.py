from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QBrush, QPen, QColor, QFont
from PySide6.QtCore import Qt, QCoreApplication, QSettings

from random import choice
from english_words import english_words_set
from time import time
from statistics import mean
from string import printable


class TypingWindow(QWidget):
    def __init__(self, parent=None):
        super(TypingWindow, self).__init__(parent=parent)

        # TODO: Implement themes system
        self.config = {
            'error_color': QColor(255, 190, 190),
            'done_color': QColor(190, 255, 190),
            'secondary_color': QColor(215, 215, 215),
            'background_color': QColor(255, 255, 255),
            'primary_color': QColor(34, 34, 34),
            'dictionary': english_words_set
        }

        self.setupWindow()
        self.settings = QSettings(QCoreApplication.applicationName(), parent=self)
        self.reset()

    def paintEvent(self, event):
        self.painter = QPainter()
        self.painter.begin(self)

        # Limiting the font size to 32
        self.painter.setFont(QFont('Menlo', max(32, event.rect().height() / self.settings.value('font_factor', 6))))
        self.isEnd = self.pointer >= len(self.text)

        # Calculating line properties
        letterSize = self.painter.fontMetrics()
        textY = event.rect().height() / 2 + letterSize.height() / 4
        lineColor = self.config['done_color'] if self.isEnd else (
            self.config['error_color'] if len(self.events) > 0 and not self.events[-1][
                'correct'] else self.config['secondary_color'])
        lineWidth = letterSize.maxWidth() + self.settings.value('line_padding', 10)
        linePadding = event.rect().width() / 4
        lineX = linePadding if not self.settings.value('enable_sliding', True) else linePadding + (
                ((event.rect().width() - lineWidth) - (linePadding * 2)) / len(self.text)) * self.pointer

        # Rendering line
        self.painter.setPen(QPen(lineColor, 1, Qt.SolidLine))
        self.painter.setBrush(QBrush(lineColor, Qt.SolidPattern))
        self.painter.drawRect(lineX, 0, lineWidth, event.rect().height())

        # Primary Text
        if not self.isEnd:
            self.painter.setPen(self.config['primary_color'])
            self.painter.drawText(lineX + self.settings.value('line_padding', 10) / 2, textY, self.text[self.pointer])
            self.painter.drawText(lineX + lineWidth + self.settings.value('line_padding', 10) / 2, textY,
                                  self.text[self.pointer + 1:])

        if len(self.events) > 1:
            speed = round(60 / mean(
                [event['time'] - self.events[self.events.index(event) - 1]['time'] for event in self.events[1:]]))
            typos = len([event for event in self.events if not event['correct']])

            print('{} char/min, {} typos'.format(speed, typos))
            # TODO: Implement result screen
            #  and draw next text starting on the right

        # Typed Text
        typedTextSize = self.painter.fontMetrics().size(Qt.TextSingleLine, self.text[:self.pointer])
        self.painter.setPen(self.config['secondary_color'])
        self.painter.drawText(lineX - typedTextSize.width() - self.settings.value('line_padding', 10) / 2, textY,
                              self.text[:self.pointer])

        self.painter.end()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Return:
            self.reset()
        elif self.settings.value('enable_backspace', True) and event.key() == Qt.Key_Backspace and self.pointer > 0:
            self.pointer -= 1
        elif event.key() not in [ord(char) for char in printable] or self.isEnd:
            return
        else:
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
        self.text = ' '.join(
            [choice(list(self.config['dictionary'])).lower() for _ in range(self.settings.value('words_count', 20))])
        self.pointer = 0

    def setupWindow(self) -> None:
        self.setWindowTitle('Typetific')
        self.setMinimumSize(1100, 620)
        self.setStyleSheet('background: {}; color: {};'.format(self.config['background_color'].name(),
                                                               self.config['primary_color'].name()))


if __name__ == '__main__':
    app = QApplication()

    window = TypingWindow()
    QCoreApplication.setApplicationName(window.windowTitle())
    QCoreApplication.setOrganizationName('Breitburg Ilya')
    QCoreApplication.setOrganizationDomain('breitburg.com')

    window.show()

    app.exec_()
