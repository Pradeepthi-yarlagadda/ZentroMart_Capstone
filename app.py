import streamlit as st
from agent import grounded_reply, verify_order, make_handover, search_product

st.set_page_config(page_title='ZentroMart AI Support', page_icon='🛍️', layout='wide')
st.title('🛍️ ZentroMart — AI Customer Support Agent')
st.caption('A retrieval-grounded support assistant using the supplied synthetic capstone dataset.')

with st.sidebar:
    st.header('🔐 Secure order lookup')
    st.caption('Order details are hidden until verification succeeds. Use only synthetic dataset records.')
    order_id = st.text_input('Order ID', key='oid')
    if st.button('Start verification', use_container_width=True):
        if order_id.strip():
            st.session_state.pending_order = order_id.strip()
            st.session_state.verified_order = None
            st.info('Enter either the registered phone last 4 digits OR the delivery pincode below.')
    if st.session_state.get('pending_order'):
        proof = st.text_input('Phone last 4 digits OR delivery pincode', type='password', key='proof')
        if st.button('Verify identity', use_container_width=True):
            result = verify_order(st.session_state.pending_order, proof)
            if result.get('verified'):
                st.session_state.verified_order = result
                st.session_state.verify_attempts = 0
                st.success('Identity verified. Order details can now be displayed.')
            else:
                attempts = st.session_state.get('verify_attempts', 0) + 1
                st.session_state.verify_attempts = attempts
                st.session_state.verified_order = None
                if attempts >= 2:
                    st.session_state.pending_order = None
                    st.error('Verification failed twice. No order details can be shared. Please contact support from your registered phone.')
                else:
                    st.error('Verification failed. You have one retry.')
    order = st.session_state.get('verified_order')
    if order:
        st.success('Verified order')
        st.write('**Status:**', order.get('status'))
        st.write('**Total:** ₹', order.get('total_inr'))
        st.write('**Delivery pincode:**', order.get('delivery_pincode'))
        st.write('**Items:**')
        for item in order.get('items', []):
            st.write(f"- {item.get('title', item.get('sku'))} × {item.get('quantity', 1)}")
        st.caption('Verification state is held only in this browser session.')
    st.divider()
    st.header('🎫 Human handover')
    summary = st.text_area('Issue + checks + reason (at least 20 characters)')
    ticket_order = st.text_input('Related order ID (optional)', key='ticket_order')
    ticket_reason = st.selectbox('Reason', ['policy_exception', 'high_value_damage', 'security_concern', 'repeat_contact', 'refund_delay', 'customer_requested_human', 'unknown'])
    if st.button('Create support ticket', use_container_width=True):
        ticket = make_handover(summary, ticket_order or None, ticket_reason, 'human_handover')
        if ticket.get('created'):
            st.success(f"Ticket created: {ticket['ticket_id']}")
        else:
            st.error(ticket.get('error', 'Ticket could not be created.'))

if 'messages' not in st.session_state:
    st.session_state.messages = []
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])
        if msg.get('sources'):
            with st.expander('Knowledge sources used'):
                for src in msg['sources']:
                    st.write(f"**{src['section_id']}** — {src['title']} · {src['file']} · score {src['score']:.3f}")

prompt = st.chat_input('Ask about returns, refunds, delivery, payments, products...')
if prompt:
    st.session_state.messages.append({'role':'user','content':prompt})
    with st.chat_message('user'):
        st.markdown(prompt)
    with st.chat_message('assistant'):
        reply, intent, sources = grounded_reply(prompt)
        st.markdown(reply)
        st.caption(f'Detected intent: {intent}')
        if sources:
            with st.expander('Knowledge sources used'):
                for src in sources:
                    st.write(f"**{src['section_id']}** — {src['title']} · {src['file']} · score {src['score']:.3f}")
    st.session_state.messages.append({'role':'assistant','content':reply,'sources':sources})

st.divider()
st.subheader('🔎 Product catalogue search')
pq = st.text_input('Search product name, brand or SKU')
if pq:
    products = search_product(pq)
    if products:
        st.dataframe(products, use_container_width=True)
    else:
        st.info('No matching product found in the supplied catalogue.')
st.caption('Educational prototype only. The dataset is synthetic; mock identity verification is not production-grade authentication.')
