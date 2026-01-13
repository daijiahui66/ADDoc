import request from './request'

export const getRecentActivities = (limit = 10) => {
  return request.get('/api/activity/latest', {
    params: { limit }
  })
}

export const getContributionData = () => {
  return request.get('/api/activity/heatmap')
}
