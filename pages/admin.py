"""Admin: log in with password from secrets.toml (ADMIN_PASSWORD); upgrade requests with receipt, change user plan, stats."""
import os
import streamlit as st
from services.auth import is_admin_logged_in, check_admin_password
from db.queries import (
    list_upgrade_requests,
    update_upgrade_request,
    set_user_plan,
    ensure_user,
)
from db.schema import get_conn


def run():
    st.title("🔐 Admin")

    # Admin login: password from secrets.toml
    try:
        admin_pass = st.secrets.get("ADMIN_PASSWORD", "")
    except Exception:
        admin_pass = ""

    if not is_admin_logged_in():
        st.markdown(
            """
            <div style="
                background: #1e293b; border-radius: 12px; padding: 1.5rem; margin: 0 0 1rem 0;
                border-left: 4px solid #06b6d4; box-shadow: 0 4px 14px rgba(0,0,0,0.25);
            ">
                <h2 style="color: #f1f5f9; margin: 0 0 0.5rem 0;">Log in to Admin</h2>
                <p style="color: #94a3b8; margin: 0; font-size: 0.9rem;">Password is set in .streamlit/secrets.toml (ADMIN_PASSWORD).</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("admin_login_form"):
            p = st.text_input("Admin password", type="password", key="admin_pw", placeholder="Enter password from secrets.toml")
            if st.form_submit_button("Login"):
                if check_admin_password(p, admin_pass):
                    st.session_state["admin_logged_in"] = True
                    st.success("Logged in.")
                    st.rerun()
                else:
                    st.error("Invalid password.")
        return

    if st.button("Logout (Admin)", key="admin_logout"):
        st.session_state["admin_logged_in"] = False
        st.rerun()

    tab1, tab2, tab3 = st.tabs(["Upgrade requests", "Users", "Stats"])

    with tab1:
        status_filter = st.selectbox("Filter", ["pending", "approved", "rejected", "all"], key="admin_status")
        status = None if status_filter == "all" else status_filter
        requests = list_upgrade_requests(status=status)
        for req in requests:
            with st.expander(f"#{req['id']} — {req['email']} — {req['plan']} — {req['status']}"):
                st.write(f"**Method:** {req.get('method')} | **Ref:** {req.get('ref') or '—'} | **TS:** {req.get('ts')}")
                # Display uploaded receipt if path exists and file is present
                receipt_path = (req.get("receipt_path") or "").strip()
                if receipt_path and os.path.isfile(receipt_path):
                    st.subheader("Uploaded receipt")
                    try:
                        st.image(receipt_path, use_container_width=True)
                    except Exception:
                        st.caption(f"File: {receipt_path}")
                elif receipt_path:
                    st.caption(f"Receipt path (file not found): {receipt_path}")
                if req["status"] == "pending":
                    st.markdown("---")
                    approved_until = st.text_input("Premium until (YYYY-MM-DD)", key=f"until_{req['id']}", placeholder="e.g. 2025-12-31")
                    if st.button("Approve", key=f"approve_{req['id']}"):
                        ensure_user(req["email"])
                        update_upgrade_request(
                            req["id"],
                            status="approved",
                            approved_until=approved_until or None,
                        )
                        set_user_plan(req["email"], req["plan"], premium_until=approved_until or None)
                        st.success("Approved.")
                        st.rerun()
                    if st.button("Reject", key=f"reject_{req['id']}"):
                        update_upgrade_request(req["id"], status="rejected")
                        st.rerun()

    with tab2:
        st.subheader("Users")
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT email, plan, premium_until, created_at FROM users ORDER BY created_at DESC LIMIT 50")
        rows = cur.fetchall()
        conn.close()
        for row in rows:
            st.write(f"**{row['email']}** — {row['plan']} — until {row['premium_until'] or '—'} — {row['created_at']}")
        st.markdown("---")
        st.subheader("Change user plan")
        with st.form("admin_change_plan"):
            change_email = st.text_input("User email", key="admin_change_email", placeholder="user@example.com")
            change_plan = st.selectbox("New plan", ["free", "premium", "pro"], key="admin_change_plan")
            change_until = st.text_input("Premium until (YYYY-MM-DD, leave empty for free)", key="admin_change_until", placeholder="e.g. 2025-12-31")
            if st.form_submit_button("Update plan"):
                if not change_email or not change_email.strip():
                    st.error("Enter user email.")
                else:
                    ensure_user(change_email.strip())
                    set_user_plan(
                        change_email.strip(),
                        change_plan,
                        premium_until=change_until.strip() or None,
                    )
                    st.success(f"Updated {change_email} to {change_plan}" + (f" until {change_until}" if change_until else "."))
                    st.rerun()

    with tab3:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS n FROM scans")
        total_scans = cur.fetchone()["n"]
        cur.execute("SELECT COUNT(*) AS n FROM users")
        total_users = cur.fetchone()["n"]
        conn.close()
        st.metric("Total scans", total_scans)
        st.metric("Total users", total_users)
