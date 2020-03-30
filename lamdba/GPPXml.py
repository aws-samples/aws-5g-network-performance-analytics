# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


class MeasCollect:

    def __init__(self, mc):

        try:
            b = mc.get('@beginTime')
        except NameError:
            b = None

        self.beginTime = b if b is not None else ''

        try:
            e = mc.get('@endTime')
        except NameError:
            e = None

        self.endTime = e if e is not None else ''

    def print(self):
        print(__class__.__name__+" - beginTime : "+self.beginTime)
        print(__class__.__name__+" - endTime : "+self.endTime)


class FileSender:

    def __init__(self, fs):
        self.localDn = fs.get('@localDn') if fs.get('@localDn') is not None else ''
        self.elementType = fs.get('@elementType') if fs.get('@elementType') is not None else ''

    def print(self):
        print(__class__.__name__+" - localDn     : "+self.localDn)
        print(__class__.__name__+" - elementType : "+self.elementType)


class FileHeader:

    def __init__(self, fh):
        self.fileFormatVersion = fh.get('@fileFormatVersion')
        self.vendorName = fh.get('@vendorName') if fh.get('@vendorName') is not None else ''
        self.dnPrefix = fh.get('@dnPrefix') if fh.get('@dnPrefix') is not None else ''
        self.fileSender = FileSender(fh.get('fileSender'))
        self.measCollect = MeasCollect(fh.get('measCollec'))

    def print(self):
        print(" ======= FileHeader =======")
        print(__class__.__name__+" - fileFormatVersion : "+self.fileFormatVersion)
        print(__class__.__name__+" - vendorName        : "+self.vendorName)
        print(__class__.__name__+" - dnPrefix          : "+self.dnPrefix)
        self.fileSender.print()
        self.measCollect.print()


class FileFooter:

    def __init__(self, ff):
        self.measCollec = MeasCollect(ff.get('measCollec'))

    def print(self):
        print(" ======= FileFooter =======")
        self.measCollec.print()


class ManagedElement:

    def __init__(self, me):
        self.localDn = me.get('@localDn') if me.get('@localDn') is not None else ''
        self.userLabel = me.get('@userLabel') if me.get('@userLabel') is not None else ''
        self.swVersion = me.get('@swVersion') if me.get('@swVersion') is not None else ''

    def print(self):
        print(__class__.__name__ + " - localDn          : " + self.localDn)
        print(__class__.__name__ + " - userLabel          : " + self.userLabel)
        print(__class__.__name__ + " - swVersion          : " + self.swVersion)


class Job:

    def __init__(self, job):
        if job is not None:
            self.jobId = job.get('@jobId') if job.get('@jobId') is not None else ''
        else:
            self.jobId = ''

    def print(self):
        print(__class__.__name__ + " - jobId          : " + self.jobId)


class GranPeriod:

    def __init__(self, gp):
        self.duration = gp.get('@duration')
        self.endTime = gp.get('@endTime')

    def print(self):
        print(__class__.__name__ + " - duration          : " + self.duration)
        print(__class__.__name__ + " - endTime          : " + self.endTime)


class RepPeriod:

    def __init__(self, rp):
        self.duration = rp.get('@duration')

    def print(self):
        print(__class__.__name__ + " - duration          : " + self.duration)


class MeasType:

    def __init__(self, n, p):
        self.name = n
        self.p = p

    def print(self):
        print(__class__.__name__ + " - name : " + self.name)
        print(__class__.__name__ + " - p    : " + str(self.p))


class MeasValue:

    def __init__(self, measobjldn, value, p, suspect=None):
        self.measObjLdn = measobjldn
        self.value = value
        self.p = p
        self.suspect = suspect

    def print(self):
        print(__class__.__name__ + " - measObjLdn : " + str(self.measObjLdn))
        print(__class__.__name__ + " - value      : " + str(self.value))
        print(__class__.__name__ + " - p          : " + str(self.p))
        print(__class__.__name__ + " - suspect    : " + str(self.suspect))


class MeasInfo:

    def __init__(self, mi):

        self.measInfoId = mi.get('@measInfoId') if mi.get('@measInfoId') is not None else ''
        self.job = Job(mi.get('job') if mi.get('job') is not None else None)
        self.granPeriod = GranPeriod(mi.get('granPeriod'))
        self.repPeriod = RepPeriod(mi.get('repPeriod') if mi.get('repPeriod') is not None else None)

        # MeasType(s)
        self.measureTypes = {}

        try:
            mts = mi.get('measTypes')
        except NameError:
            mts = None

        if mts is not None:
            for i in range(len(mts.split(' '))):
                self.measureTypes[i] = MeasType(mts.split(' ')[i], None)
        else:
            mt = mi.get('measType')
            if isinstance(mt, dict):
                self.measureTypes[0] = MeasType(mt.get('#text'), mt.get('@p'))
            if isinstance(mt, list):
                for i in range(len(mt)):
                    self.measureTypes[i] = MeasType(mt[i].get('#text'), mt[i].get('@p'))

        # MeasValue
        self.measValues = {}

        mv = mi.get('measValue')

        if mv is not None and isinstance(mv, dict):

            if "measResults" in mv:

                mrs = mv.get('measResults').split(' ')

                for i in range(len(mrs)):
                    self.measValues[len(self.measValues)] = MeasValue(mv.get('@measObjLdn'),
                                                                      mrs[i],
                                                                      mv.get('@p'),
                                                                      mv.get('suspect'))
            else:
                if isinstance(mv.get('r'), dict):
                    self.measValues[0] = MeasValue(mv.get('@measObjLdn'),
                                                   mv.get('r').get('#text'),
                                                   mv.get('r').get('@p'),
                                                   mv.get('suspect'))

                elif isinstance(mv.get('r'), list):
                    pass

        elif mv is not None and isinstance(mv, list):
            for i in range(len(mv)):

                if "measResults" in mv[i]:
                    mrs = mv[i].get('measResults').split(' ')

                    for j in range(len(mrs)):
                        self.measValues[len(self.measValues)] = MeasValue(mv[i].get('@measObjLdn'),
                                                                          mrs[j],
                                                                          mv[i].get('@p'),
                                                                          mv[i].get('suspect'))
                else:
                    if isinstance(mv[i].get('r'), dict):
                        self.measValues[i] = MeasValue(mv[i].get('@measObjLdn'),
                                                       mv[i].get('r').get('#text'),
                                                       mv[i].get('r').get('@p'),
                                                       mv[i].get('suspect'))

                    elif isinstance(mv[i].get('r'), list):
                        for j in range(len(mv[i].get('r'))):
                            self.measValues[len(self.measValues)] = MeasValue(mv[i].get('@measObjLdn'),
                                                                              mv[i].get('r')[j].get('#text'),
                                                                              mv[i].get('r')[j].get('@p'),
                                                                              mv[i].get('suspect'))

    def print(self):
        print(__class__.__name__ + " - measInfoId          : " + self.measInfoId)
        self.job.print()
        self.granPeriod.print()
        self.repPeriod.print()

        for i in range(len(self.measureTypes)):
            self.measureTypes[i].print()

        for i in range(len(self.measValues)):
            self.measValues[i].print()


class MeasData:

    def __init__(self,md):
        self.managedElemend = ManagedElement(md.get('managedElement'))

        try:
            mi = md.get('measInfo')
        except NameError:
            mi = None

        self.measInfo = {}

        if mi is not None and isinstance(mi, dict):
            self.measInfo[0] = MeasInfo(mi)

        elif mi is not None and isinstance(mi, list):
            for i in range(len(mi)):
                self.measInfo[i] = MeasInfo(mi[i])

    def print(self):
        print(" ======= MeasData =======")
        self.managedElemend.print()

        for i in range(len(self.measInfo)):
            self.measInfo[i].print()


class GPPXml:

    def __init__(self, x):
        self.fileHeader = FileHeader(x.get('fileHeader'))
        self.fileFooter = FileFooter(x.get('fileFooter'))

        try:
            md = x.get('measData')
        except NameError:
            md = None

        self.measData = {}

        if md is not None and isinstance(md, dict):
            self.measData[0] = MeasData(md)

        elif md is not None and isinstance(md, list):
            for i in range(len(md)):
                self.measData[i] = MeasData(md[i])

    def get_no_of_meas_data(self):
        return len(self.measData)

    def get_no_of_meas_info(self):
        n = 0
        for i in range(self.get_no_of_meas_data()):
            n += len(self.measData[i].measInfo)

        return n

    def print(self):
        print(" ============== GPPXml ==============")
        self.fileHeader.print()
        self.fileFooter.print()

        for i in range(len(self.measData)):
            self.measData[i].print()

    def convert_to_records(self, input_file, input_date_time, transformed_file):

        header = self.get_record_header()

        records = []

        head_foot = dict()
        head_foot[header[0]] = self.fileHeader.fileFormatVersion
        head_foot[header[1]] = self.fileHeader.vendorName
        head_foot[header[2]] = self.fileHeader.dnPrefix
        head_foot[header[3]] = self.fileHeader.fileSender.localDn
        head_foot[header[4]] = self.fileHeader.fileSender.elementType
        head_foot[header[5]] = self.fileHeader.measCollect.beginTime
        head_foot[header[6]] = self.fileFooter.measCollec.endTime

        for i in range(len(self.measData)):
            md = self.measData[i]

            meas_data = dict()
            meas_data[header[7]] = md.managedElemend.localDn
            meas_data[header[8]] = md.managedElemend.userLabel
            meas_data[header[9]] = md.managedElemend.swVersion

            for j in range(len(md.measInfo)):
                mi = md.measInfo[j]

                meas_info = dict()
                meas_info[header[10]] = mi.measInfoId
                meas_info[header[11]] = mi.job.jobId
                meas_info[header[12]] = mi.granPeriod.duration
                meas_info[header[13]] = mi.granPeriod.endTime
                meas_info[header[14]] = mi.repPeriod.duration

                for k in range(len(mi.measValues)):
                    mv = mi.measValues[k]
                    mt = mi.measureTypes[k%len(mi.measureTypes)]

                    measure = dict()
                    measure[header[15]] = mv.measObjLdn
                    measure[header[16]] = mt.name
                    measure[header[17]] = int(mv.value)
                    measure[header[18]] = mv.p
                    measure[header[19]] = mv.suspect
                    
                    file_details = dict()
                    file_details[header[20]] = input_file
                    file_details[header[21]] = input_date_time
                    file_details[header[22]] = transformed_file

                    record = dict()
                    record.update(head_foot)
                    record.update(meas_data)
                    record.update(meas_info)
                    record.update(measure)
                    record.update(file_details)

                    records.append(record)

        return records

    @staticmethod
    def get_record_header():

        return [
            "fh_file_format_version",
            "fh_vendor_name",
            "fh_dn_prefix",
            "fh_fs_local_dn",
            "fh_fs_element_type",
            "fh_mc_begin_time",
            "ff_mc_end_time",
            "md_me_local_dn",
            "md_me_user_label",
            "md_me_sw_version",
            "md_mi_meas_info_id",
            "md_mi_job_jobid",
            "md_mi_gp_duration",
            "md_mi_gp_end_time",
            "md_mi_rp_duration",
            "md_mi_meas_obj_ldn",
            "md_mi_meas_name",
            "md_mi_meas_value",
            "md_mi_meas_p",
            "md_mi_meas_suspect",
            "input_file",
            "input_date_time",
            "transformed_file"
        ]
