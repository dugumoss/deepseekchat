import pysrt
from datetime import timedelta
from dsChat import get_deepseek, msSRT

def split_str(s_list: list, s: str):
    for x in s_list:
        if x in s:
            return s.split(x), x
    return [s], ''

def convert_subriptime_to_timedelta(subrip_time):
    """将 SubRipTime 转换为 timedelta（以毫秒为单位）"""
    return timedelta(hours=subrip_time.hours, minutes=subrip_time.minutes, seconds=subrip_time.seconds, milliseconds=subrip_time.milliseconds)

def convert_timedelta_to_subriptime(td):
    """将 timedelta 转换为 SubRipTime"""
    total_milliseconds = int(td.total_seconds() * 1000)
    hours, remainder = divmod(total_milliseconds, 3600000)
    minutes, remainder = divmod(remainder, 60000)
    seconds, milliseconds = divmod(remainder, 1000)
    return pysrt.SubRipTime(hours, minutes, seconds, milliseconds)

def convert_srt(src_file, dst_file):
    # 读取 SRT 文件
    subs = pysrt.open(src_file)

    merged_subs = []
    current_sub = None
    start_time = None
    line = ''
    # 打印每个字幕条目的内容和时间戳
    for sub in subs:
        temp = sub.text.strip()

        # 检查是否包含句号、问号或感叹号
        if '.' in temp or '?' in temp or '!' in temp:
            l, ext = split_str(['.', '?', '!'], temp)
            # 如果当前字幕为空，初始化
            if current_sub is None:
                current_sub = sub
                current_sub.text = line + ' ' + l[0] + ext
                line = ''
                if start_time is not None:
                    current_sub.start = start_time
                    start_time = None
            else:
                # 合并时间戳
                current_sub.end = sub.end  # 更新结束时间为当前字幕的结束时间
                current_sub.text += line + ' ' + l[0] + ext # 合并文本

            current_sub.text = current_sub.text.strip()

            # 如果当前字幕以标点符号结尾，保存并重置
            if temp.endswith(('.', '?', '!')):
                merged_subs.append(current_sub)
                current_sub = None
                line = ''
            else:
                tmp1 = len(l[0].strip())
                tmp2 = len(l[1].strip())

                if tmp2 > 0:
                    # 计算当前字幕的持续时间（秒）
                    duration = (sub.end.hours * 3600 + sub.end.minutes * 60 + sub.end.seconds) - \
                    (sub.start.hours * 3600 + sub.start.minutes * 60 + sub.start.seconds)
                    # 计算当前字幕的结束时间
                    current_sub.end = convert_timedelta_to_subriptime(convert_subriptime_to_timedelta(sub.start) + timedelta(seconds=duration * tmp1/(tmp1+tmp2)))

                merged_subs.append(current_sub)

                start_time = current_sub.end
                current_sub = None
                line = l[1]
        else:
            # 如果没有标点符号，继续合并
            if current_sub is None:
                current_sub = sub
                current_sub.text = line + ' ' + current_sub.text
                line = ''
                if start_time is not None:
                    current_sub.start = start_time
                    start_time = None
            else:
                current_sub.text += line + ' ' + temp  # 合并文本
                line = ''

    pysrt.SubRipFile(merged_subs).save(dst_file)

def translate_srt(src_file, dst_file):
    deepseek = get_deepseek()
    # 读取 SRT 文件
    subs = pysrt.open(src_file)
    # 翻译
    for sub in subs:
        sub.text = deepseek.deepseek_to_chat(sub.text, msSRT)
    deepseek.clear()

    # 保存
    pysrt.SubRipFile(subs).save(dst_file)

