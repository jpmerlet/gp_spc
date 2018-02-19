# -*- coding: utf-8 -*-
class DXF:

    @staticmethod
    def read(path):
        i = 0
        lines = []
        infile = open(path, 'r')
        for line in infile:
            line = line.replace('\n', '')
            line = line.strip()
            if i % 2 == 0:
                type_ = line
            else:
                lines.append((type_, line))
            i += 1
        infile.close()

        return lines