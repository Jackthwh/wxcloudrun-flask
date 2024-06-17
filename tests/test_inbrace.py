from pathlib import Path

from wxcloudrun.dao import delete_demobyuser, insert_demo, query_demobyuser
from wxcloudrun.inbrace import Inbrace
from wxcloudrun.model import Demos
from wxcloudrun.open_ai import OpenAIClient
from wxcloudrun.receive import parse_xml

def test_inbrace():
    demo = Demos()
    demo.thread_id = 'thread_FD77xJtVZveAbyNPzFviBoNn'
    ib = Inbrace(demo)
    assert ib

def test_dup_predefined():
    ib = Inbrace(None)
    assert not ib.get_current_thread()
    ib.dup_predefined_thread()
    assert ib.get_current_thread()

def test_handle_new():
    file_path = Path('tests/data/new_thread.msg')
    file_content = file_path.read_text()
    msg = parse_xml(file_content)

    demo = Demos()
    demo.user = 'Jack'
    demo.demo = 'Inbrace'
    delete_demobyuser(demo.user)
    insert_demo(demo)

    ib = Inbrace(None)
    ret = ib.handle(msg)
    assert ret == OpenAIClient.greeting
    demo = query_demobyuser(demo.user)
    assert demo.thread_id == ib.get_current_thread().id

def test_handle_image_history():
    file_path = Path('tests/data/image_2_thread.msg')
    file_content = file_path.read_text()
    msg = parse_xml(file_content)

    demo = Demos()
    demo.user = 'Jack'
    demo.demo = 'Inbrace'
    delete_demobyuser(demo.user)
    insert_demo(demo)

    ib = Inbrace(None)
    ret = ib.handle(msg)
    assert 'Showing LR1 is blocked out' in ret
    demo = query_demobyuser(demo.user)
    assert demo.thread_id == ib.get_current_thread().id

def test_handle_question():
    file_path = Path('tests/data/new_thread.msg')
    file_content = file_path.read_text()
    new_msg = parse_xml(file_content)

    file_path = Path('tests/data/image_question1.msg')
    file_content = file_path.read_text()
    image_msg = parse_xml(file_content)

    file_path = Path('tests/data/question1.msg')
    file_content = file_path.read_text()
    msg = parse_xml(file_content)

    demo = Demos()
    demo.user = 'Jack'
    demo.demo = 'Inbrace'
    delete_demobyuser(demo.user)
    insert_demo(demo)

    ib = Inbrace(None)
    ib.handle(new_msg)
    assert ib.get_current_thread()
    ret = ib.handle(image_msg)
    assert ret == ""
    ret = ib.handle(msg)
    assert 'The image indicates' in ret