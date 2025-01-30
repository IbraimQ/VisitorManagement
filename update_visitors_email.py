@app.route('/update_visit_status/<int:visit_id>', methods=['POST'])
def update_visit_status(visit_id):
    if 'manager_id' not in session:
        return redirect(url_for('login'))
    visit = Visit.query.get_or_404(visit_id)
    visitor = Visitor.query.get_or_404(visit.VisitorID)
    status = request.form['status']
    visit.ApprovalStatus = status
    db.session.commit()

    # Send email notification to visitor
    subject = "Visit Status Update"
    body = f"""
    <html>
    <body>
        <p>Dear {visitor.FirstName} {visitor.LastName},</p>
        <p>Your visit scheduled for {visit.VisitDate} has been {status.lower()}.</p>
        <p>Thank you.</p>
    </body>
    </html>
    """
    msg = Message(subject, sender='ihemaa.4@gmail.com', recipients=[visitor.Email])
    msg.body = f"Your visit scheduled for {visit.VisitDate} has been {status.lower()}."
    msg.html = body

    try:
        mail.send(msg)
    except Exception as e:
        return str(e)

    return redirect(url_for('manager_dashboard'))
