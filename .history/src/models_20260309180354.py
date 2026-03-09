class Link(Base):
    __tablename__ = "links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    short_code = Column(String(10), unique=True, index=True)
    original_url = Column(Text, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    is_anonymous = Column(Boolean, default=True, nullable=False)  # ← КЛЮЧЕВОЕ ИЗМЕНЕНИЕ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    click_count = Column(Integer, default=0)
    last_used_at = Column(DateTime(timezone=True))
    deleted_at = Column(DateTime(timezone=True))
