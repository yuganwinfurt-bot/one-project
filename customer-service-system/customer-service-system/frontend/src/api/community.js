import request from '@/utils/request'

export const getCustomerProfile = id => request.get(`/api/community/users/${id}`)
export const createDirectConversation = userId => request.post('/api/community/conversations', { user_id: userId })
export const getDirectMessages = id => request.get(`/api/community/conversations/${id}/messages`)
export const sendDirectMessage = (id, content) => request.post(`/api/community/conversations/${id}/messages`, { content })
export const postReviewComment = (id, content, replyToUserId) => request.post(`/api/community/reviews/${id}/comments`, { content, reply_to_user_id: replyToUserId || null })
export const readReviewNotification = id => request.post(`/api/community/notifications/${id}/read`)
