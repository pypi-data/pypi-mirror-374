

class Inquiry:
    def __init__(self, *, inquiry: str = None, member: str = None):
        self.inquiry = inquiry
        self.member = member

    def set_inquiry(self, inquiry: str):
        self.inquiry = inquiry

    def set_member(self, member: str):
        self.member = member

