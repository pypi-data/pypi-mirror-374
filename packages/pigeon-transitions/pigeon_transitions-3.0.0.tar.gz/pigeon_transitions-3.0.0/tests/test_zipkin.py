from pigeon_transitions import BaseMachine, RootMachine
from py_zipkin.transport import BaseTransportHandler
import json
from threading import Thread
from py_zipkin.zipkin import create_http_headers_for_new_span
import pytest


def test_zipkin_states(mocker):
    class TestState(BaseMachine.state_cls):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.start_span = mocker.MagicMock()
            self.stop_span = mocker.MagicMock()

    class TestMachine(BaseMachine):
        state_cls = TestState

    class TestRoot(RootMachine):
        state_cls = TestState

    child3 = TestMachine(
        states=[
            "eight",
            "nine",
            "ten",
        ],
        initial="eight",
        transitions=[
            {
                "source": "eight",
                "dest": "nine",
                "trigger": "change",
            },
            {
                "source": "nine",
                "dest": "ten",
                "trigger": "change",
            },
        ],
    )

    child2 = TestMachine(
        states=[
            {
                "name": "five",
                "children": child3,
                "remap": {
                    "ten": "six",
                },
            },
            "six",
        ],
        initial="five",
    )

    child1 = TestMachine(
        states=[
            "three",
            {
                "name": "four",
                "children": child2,
                "remap": {
                    "six": "seven",
                },
            },
            "seven",
        ],
        initial="three",
        transitions=[
            {
                "source": "three",
                "dest": "four",
                "trigger": "go",
            },
        ],
    )

    machine = TestRoot(
        states=[
            "one",
            {
                "name": "two",
                "children": child1,
                "remap": {
                    "seven": "one",
                },
            },
        ],
        initial="one",
        transitions=[
            {
                "source": "one",
                "dest": "two",
                "trigger": "start",
            },
            {
                "source": "one",
                "dest": "two_four_five",
                "trigger": "jump",
            },
        ],
    )

    machine._zipkin_transport = True
    machine._start()

    machine.get_state("one").start_span.assert_called_once()

    assert machine.start()
    assert machine.state == "two_three"

    machine.get_state("one").start_span.assert_called_once()
    machine.get_state("one").stop_span.assert_called_once()
    machine.get_state("two").start_span.assert_called_once()
    machine.get_state("two_three").start_span.assert_called_once()

    assert machine.go()
    assert machine.state == "two_four_five_eight"

    machine.get_state("one").stop_span.assert_called_once()
    machine.get_state("two").start_span.assert_called_once()
    machine.get_state("two_three").start_span.assert_called_once()
    machine.get_state("two_three").stop_span.assert_called_once()
    machine.get_state("two_four").start_span.assert_called_once()
    machine.get_state("two_four_five").start_span.assert_called_once()
    machine.get_state("two_four_five_eight").start_span.assert_called_once()

    assert machine.change()
    assert machine.state == "two_four_five_nine"

    machine.get_state("two_three").stop_span.assert_called_once()
    machine.get_state("two_four").start_span.assert_called_once()
    machine.get_state("two_four_five").start_span.assert_called_once()
    machine.get_state("two_four_five_eight").start_span.assert_called_once()
    machine.get_state("two_four_five_eight").stop_span.assert_called_once()
    machine.get_state("two_four_five_nine").start_span.assert_called_once()

    machine.get_state("one").start_span.reset_mock()
    machine.get_state("one").stop_span.reset_mock()

    assert machine.change()
    assert machine.state == "one"

    machine.get_state("two_four_five_eight").stop_span.assert_called_once()
    machine.get_state("two_four_five_nine").start_span.assert_called_once()
    machine.get_state("two_four_five_nine").stop_span.assert_called_once()
    machine.get_state("one").start_span.assert_called_once()
    machine.get_state("one").stop_span.assert_not_called()

    assert machine.jump()
    assert machine.state == "two_four_five_eight"

    machine.get_state("two").stop_span.reset_mock()
    machine.get_state("two_four").stop_span.reset_mock()
    machine.get_state("two_four_five").stop_span.reset_mock()
    machine.get_state("two_four_five_eight").stop_span.reset_mock()

    machine.stop_all_spans()

    machine.get_state("two").stop_span.assert_called_once()
    machine.get_state("two_four").stop_span.assert_called_once()
    machine.get_state("two_four_five").stop_span.assert_called_once()
    machine.get_state("two_four_five_eight").stop_span.assert_called_once()


def test_zipkin_state_re_enter(mocker):
    class TestState(BaseMachine.state_cls):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.start_span = mocker.MagicMock()
            self.stop_span = mocker.MagicMock()

    class TestMachine(BaseMachine):
        state_cls = TestState

    class TestRoot(RootMachine):
        state_cls = TestState

    child = TestMachine(
        states=[
            "one",
            "two",
        ],
        initial="one",
        transitions=[
            {
                "source": "one",
                "dest": "two",
                "trigger": "go",
            },
        ],
    )

    machine = TestRoot(
        states=[
            "one",
            {
                "name": "two",
                "children": child,
                "remap": {
                    "two": "two",
                },
            },
        ],
        initial="one",
        transitions=[
            {
                "source": "one",
                "dest": "two",
                "trigger": "start",
            },
        ],
    )

    machine._zipkin_transport = True
    machine._start()

    machine.get_state("one").start_span.assert_called_once()

    assert machine.start()
    assert machine.state == "two_one"

    machine.get_state("one").start_span.assert_called_once()
    machine.get_state("one").stop_span.assert_called_once()
    machine.get_state("two").start_span.assert_called_once()
    machine.get_state("two_one").start_span.assert_called_once()

    machine.get_state("two").start_span.reset_mock()
    machine.get_state("two_one").start_span.reset_mock()

    assert machine.go()
    assert machine.state == "two_one"

    machine.get_state("one").stop_span.assert_called_once()
    machine.get_state("two").stop_span.assert_called_once()
    machine.get_state("two").start_span.assert_called_once()
    machine.get_state("two_one").stop_span.assert_called_once()
    machine.get_state("two_one").start_span.assert_called_once()


@pytest.mark.xfail
def test_zipkin_callbacks(mocker):
    tracer = mocker.MagicMock()

    mocker.patch("pigeon_transitions.root.Tracer", tracer)

    class State(BaseMachine.state_cls):
        def start_span(self, *args, **kwargs):
            pass

        def stop_span(self, *args, **kwargs):
            pass

    class Child(BaseMachine):
        state_cls = State

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def callback1(self):
            pass

        def callback2(self):
            pass

        def callback3(self):
            pass

    child = Child(
        states=[
            "two",
            "three",
            {
                "name": "four",
                "on_enter": "callback3",
            },
        ],
        initial="two",
        transitions=[
            {
                "source": "two",
                "dest": "three",
                "trigger": "change",
                "before": "callback2",
            },
            {
                "source": "three",
                "dest": "four",
                "trigger": "change",
            },
        ],
        on_enter="callback1",
    )

    class Root(RootMachine):
        state_cls = State

    root = Root(
        states=[
            {
                "name": "one",
                "children": child,
            },
        ],
        initial="one",
    )

    root._start()

    assert root.state == "one_two"

    tracer().zipkin_span.assert_called_with(
        "pigeon-transitions", span_name="callback callback1"
    )
    tracer().zipkin_span().__enter__.assert_called_once()
    tracer().zipkin_span().__exit__.assert_called_once()

    tracer().zipkin_span().__enter__.reset_mock()
    tracer().zipkin_span().__exit__.reset_mock()

    assert root.change()
    assert root.state == "one_three"

    tracer().zipkin_span.assert_called_with(
        "pigeon-transitions", span_name="callback callback2"
    )
    tracer().zipkin_span().__enter__.assert_called_once()
    tracer().zipkin_span().__exit__.assert_called_once()

    tracer().zipkin_span().__enter__.reset_mock()
    tracer().zipkin_span().__exit__.reset_mock()

    assert root.change()
    assert root.state == "one_four"

    tracer().zipkin_span.assert_called_with(
        "pigeon-transitions", span_name="callback callback3"
    )
    tracer().zipkin_span().__enter__.assert_called_once()
    tracer().zipkin_span().__exit__.assert_called_once()

    tracer().zipkin_span().__enter__.reset_mock()
    tracer().zipkin_span().__exit__.reset_mock()


class MockTransport(BaseTransportHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.batches = []

    def get_max_payload_bytes(self):
        return None

    def send(self, batch):
        self.batches.append(json.loads(batch))


def run_in_thread(func, *args, **kwargs):
    if len(args) or len(kwargs):
        raise NotImplementedError()
    thread = Thread(target=func)
    thread.start()
    thread.join()


def test_integration(mocker):
    mocker.patch("pigeon_transitions.root.setup_zipkin_transport", MockTransport)

    child = BaseMachine(
        states=[
            "two",
            "three",
            "four",
        ],
        initial="two",
        transitions=[
            {
                "source": "two",
                "dest": "three",
                "trigger": "change",
            },
            {
                "source": "three",
                "dest": "four",
                "trigger": "change",
            },
        ],
    )

    root = RootMachine(
        states=[
            "one",
            {"name": "two", "children": child, "remap": {"four": "three"}},
            "three",
        ],
        transitions=[
            {
                "source": "one",
                "dest": "two",
                "trigger": "change",
            },
        ],
        initial="one",
    )

    assert len(root._zipkin_transport.batches) == 0

    root._start()
    assert root.state == "one"

    assert len(root._zipkin_transport.batches) == 0

    run_in_thread(root.change)
    assert root.state == "two_two"

    assert len(root._zipkin_transport.batches) == 1

    batch = root._zipkin_transport.batches[-1]
    assert len(batch) == 1
    span = batch[0]
    assert span["name"] == "one"
    assert "parentId" not in span
    trace_id = span["traceId"]

    run_in_thread(root.change)
    assert root.state == "two_three"

    assert len(root._zipkin_transport.batches) == 1

    run_in_thread(root.change)
    assert root.state == "three"

    assert len(root._zipkin_transport.batches) == 2

    batch = root._zipkin_transport.batches[-1]
    assert len(batch) == 3

    root_span = batch[-1]
    assert "parentId" not in root_span
    assert root_span["name"] == "two"
    assert root_span["traceId"] != trace_id
    trace_id = root_span["traceId"]

    span_two = batch[0]
    assert span_two["name"] == "two_two"
    assert span_two["traceId"] == trace_id
    assert span_two["parentId"] == root_span["id"]

    span_three = batch[1]
    assert span_three["name"] == "two_three"
    assert span_three["traceId"] == trace_id
    assert span_three["parentId"] == root_span["id"]


@pytest.mark.xfail
def test_create_zipkin_headers(mocker):
    mocker.patch("pigeon_transitions.root.setup_zipkin_transport", MockTransport)

    class TestMachine(BaseMachine):
        def __init__(self):
            self.headers = None
            super().__init__(
                states=[
                    {
                        "name": "one",
                        "on_enter": self.create_headers,
                    }
                ],
                initial="one",
            )

        def create_headers(self):
            self.headers = create_http_headers_for_new_span()

    child = TestMachine()

    root = RootMachine(
        states=[
            "one",
            {
                "name": "two",
                "children": child,
            },
        ],
        initial="one",
        transitions=[
            {
                "source": "one",
                "dest": "two",
                "trigger": "start",
            },
        ],
    )

    root._start()

    assert root.state == "one"
    assert root.start()
    assert root.state == "two_one"

    headers = child.headers

    assert child.headers is not None

    two = root.get_state("two")._span.zipkin_attrs
    two_one = root.get_state("two_one")._span.zipkin_attrs

    assert two.trace_id == two_one.trace_id
    assert two.span_id == two_one.parent_span_id

    callback = [span for span in root._zipkin_tracer.get_spans()][0]

    assert callback.name == "callback create_headers"

    assert two.trace_id == callback.trace_id
    assert two_one.span_id == callback.parent_id

    assert two.trace_id == headers["X-B3-TraceId"]
    assert callback.span_id == headers["X-B3-ParentSpanId"]


def test_start_nested(mocker):
    mocker.patch("pigeon_transitions.root.setup_zipkin_transport")

    class TestState(BaseMachine.state_cls):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.start_span = mocker.MagicMock()
            self.stop_span = mocker.MagicMock()

    class TestMachine(BaseMachine):
        state_cls = TestState

    class TestRoot(RootMachine):
        state_cls = TestState

    child = TestMachine(
        states=[
            "two",
        ],
        initial="two",
    )

    root = TestRoot(
        states=[
            {
                "name": "one",
                "children": child,
            },
        ],
        initial="one",
    )

    root._start()

    root.get_state("one").start_span.assert_called_once()
    root.get_state("one").stop_span.assert_not_called()

    root.get_state("one_two").start_span.assert_called_once()
    root.get_state("one_two").stop_span.assert_not_called()
