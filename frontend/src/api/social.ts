// ============================================================
// FitAI – Social Fitness Ecosystem API Client
// Endpoints for Friends, Follows, Feed, Challenges, Badges,
// Teams, Leaderboards, and Athlete Profiles
// ============================================================
import api from './client';
import type {
  FriendshipResponse,
  UserSearchResponse,
  FollowResponse,
  ActivityFeedResponse,
  ChallengeCreate,
  ChallengeResponse,
  ChallengeParticipantResponse,
  BadgeResponse,
  AchievementsOverviewResponse,
  TeamCreate,
  TeamResponse,
  TeamMemberResponse,
  LeaderboardEntry,
  PublicProfileResponse,
  NotificationResponse,
} from '../types';

export const socialApi = {
  // ── Friends & Search ──────────────────────────────────────────
  async sendFriendRequest(receiver_id: number): Promise<FriendshipResponse> {
    const res = await api.post<FriendshipResponse>('/social/friends/request', { receiver_id });
    return res.data;
  },

  async acceptFriendRequest(friendship_id: number): Promise<FriendshipResponse> {
    const res = await api.put<FriendshipResponse>(`/social/friends/${friendship_id}/accept`);
    return res.data;
  },

  async rejectFriendRequest(friendship_id: number): Promise<FriendshipResponse> {
    const res = await api.put<FriendshipResponse>(`/social/friends/${friendship_id}/reject`);
    return res.data;
  },

  async removeFriend(friendship_id: number): Promise<{ success: boolean; message: string }> {
    const res = await api.delete<{ success: boolean; message: string }>(`/social/friends/${friendship_id}`);
    return res.data;
  },

  async getFriends(): Promise<any[]> {
    const res = await api.get<any[]>('/social/friends');
    return res.data;
  },

  async getPendingRequests(): Promise<FriendshipResponse[]> {
    const res = await api.get<FriendshipResponse[]>('/social/friends/pending');
    return res.data;
  },

  async searchUsers(query: string): Promise<UserSearchResponse[]> {
    const res = await api.get<UserSearchResponse[]>('/social/users/search', { params: { q: query } });
    return res.data;
  },

  // ── Follow System ─────────────────────────────────────────────
  async followUser(user_id: number): Promise<FollowResponse> {
    const res = await api.post<FollowResponse>(`/social/follow/${user_id}`);
    return res.data;
  },

  async unfollowUser(user_id: number): Promise<{ success: boolean; message: string }> {
    const res = await api.delete<{ success: boolean; message: string }>(`/social/follow/${user_id}`);
    return res.data;
  },

  async getFollowers(): Promise<FollowResponse[]> {
    const res = await api.get<FollowResponse[]>('/social/followers');
    return res.data;
  },

  async getFollowing(): Promise<FollowResponse[]> {
    const res = await api.get<FollowResponse[]>('/social/following');
    return res.data;
  },

  // ── Activity Feed ─────────────────────────────────────────────
  async getGlobalFeed(limit = 50, offset = 0): Promise<ActivityFeedResponse[]> {
    const res = await api.get<ActivityFeedResponse[]>('/social/feed', { params: { limit, offset } });
    return res.data;
  },

  async getFriendsFeed(limit = 50, offset = 0): Promise<ActivityFeedResponse[]> {
    const res = await api.get<ActivityFeedResponse[]>('/social/feed/friends', { params: { limit, offset } });
    return res.data;
  },

  // ── Challenges ────────────────────────────────────────────────
  async createChallenge(data: ChallengeCreate): Promise<ChallengeResponse> {
    const res = await api.post<ChallengeResponse>('/challenges', data);
    return res.data;
  },

  async listChallenges(): Promise<ChallengeResponse[]> {
    const res = await api.get<ChallengeResponse[]>('/challenges');
    return res.data;
  },

  async getChallenge(id: number): Promise<ChallengeResponse> {
    const res = await api.get<ChallengeResponse>(`/challenges/${id}`);
    return res.data;
  },

  async joinChallenge(id: number): Promise<ChallengeParticipantResponse> {
    const res = await api.post<ChallengeParticipantResponse>(`/challenges/${id}/join`);
    return res.data;
  },

  async leaveChallenge(id: number): Promise<{ success: boolean; message: string }> {
    const res = await api.post<{ success: boolean; message: string }>(`/challenges/${id}/leave`);
    return res.data;
  },

  async getMyChallenges(): Promise<ChallengeResponse[]> {
    const res = await api.get<ChallengeResponse[]>('/challenges/my');
    return res.data;
  },

  // ── Badges & Achievements ─────────────────────────────────────
  async listBadges(): Promise<BadgeResponse[]> {
    const res = await api.get<BadgeResponse[]>('/badges');
    return res.data;
  },

  async getMyBadges(): Promise<BadgeResponse[]> {
    const res = await api.get<BadgeResponse[]>('/badges/my');
    return res.data;
  },

  async getAchievements(): Promise<AchievementsOverviewResponse> {
    const res = await api.get<AchievementsOverviewResponse>('/achievements');
    return res.data;
  },

  // ── Teams & Communities ───────────────────────────────────────
  async createTeam(data: TeamCreate): Promise<TeamResponse> {
    const res = await api.post<TeamResponse>('/teams', data);
    return res.data;
  },

  async listTeams(): Promise<TeamResponse[]> {
    const res = await api.get<TeamResponse[]>('/teams');
    return res.data;
  },

  async getTeam(id: number): Promise<TeamResponse> {
    const res = await api.get<TeamResponse>(`/teams/${id}`);
    return res.data;
  },

  async joinTeam(id: number): Promise<TeamMemberResponse> {
    const res = await api.post<TeamMemberResponse>(`/teams/${id}/join`);
    return res.data;
  },

  async leaveTeam(id: number): Promise<{ success: boolean; message: string }> {
    const res = await api.post<{ success: boolean; message: string }>(`/teams/${id}/leave`);
    return res.data;
  },

  // ── Leaderboards ──────────────────────────────────────────────
  async getStepsLeaderboard(limit = 20): Promise<LeaderboardEntry[]> {
    const res = await api.get<LeaderboardEntry[]>('/leaderboards/steps', { params: { limit } });
    return res.data;
  },

  async getWorkoutsLeaderboard(limit = 20): Promise<LeaderboardEntry[]> {
    const res = await api.get<LeaderboardEntry[]>('/leaderboards/workouts', { params: { limit } });
    return res.data;
  },

  async getXPLeaderboard(limit = 20): Promise<LeaderboardEntry[]> {
    const res = await api.get<LeaderboardEntry[]>('/leaderboards/xp', { params: { limit } });
    return res.data;
  },

  async getRecoveryLeaderboard(limit = 20): Promise<LeaderboardEntry[]> {
    const res = await api.get<LeaderboardEntry[]>('/leaderboards/recovery', { params: { limit } });
    return res.data;
  },

  async getStreaksLeaderboard(limit = 20): Promise<LeaderboardEntry[]> {
    const res = await api.get<LeaderboardEntry[]>('/leaderboards/streaks', { params: { limit } });
    return res.data;
  },

  // ── Social Notifications ──────────────────────────────────────
  async getSocialNotifications(limit = 50): Promise<NotificationResponse[]> {
    const res = await api.get<NotificationResponse[]>('/social/notifications', { params: { limit } });
    return res.data;
  },

  async markNotificationRead(id: number): Promise<NotificationResponse> {
    const res = await api.put<NotificationResponse>(`/social/notifications/${id}/read`);
    return res.data;
  },

  async markAllNotificationsRead(): Promise<{ marked_read: number }> {
    const res = await api.put<{ marked_read: number }>('/social/notifications/read-all');
    return res.data;
  },

  // ── Public Athlete Profile ────────────────────────────────────
  async getPublicProfile(username: string): Promise<PublicProfileResponse> {
    const res = await api.get<PublicProfileResponse>(`/profile/${username}`);
    return res.data;
  },
};
