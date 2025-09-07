"""
Collaboration Manager
团队协作管理器，实现高级的多Agent协作模式
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from ...framework.abstractions.agent import UniversalAgent, AgentCapability
from ...framework.abstractions.task import UniversalTask, TaskType, TaskPriority
from ...framework.abstractions.context import UniversalContext
from ...framework.abstractions.result import UniversalResult, ResultStatus

logger = logging.getLogger(__name__)


class CollaborationPattern(Enum):
    """协作模式枚举"""
    SEQUENTIAL = "sequential"  # 顺序执行
    PARALLEL = "parallel"  # 并行执行
    ROUND_ROBIN = "round_robin"  # 轮询执行
    EXPERT_CONSULTATION = "expert_consultation"  # 专家会诊
    PEER_REVIEW = "peer_review"  # 同行评议
    DEBATE = "debate"  # 辩论模式
    CONSENSUS = "consensus"  # 共识达成
    HIERARCHICAL = "hierarchical"  # 分层决策


class CollaborationRole(Enum):
    """协作角色枚举"""
    LEADER = "leader"  # 领导者
    EXPERT = "expert"  # 专家
    REVIEWER = "reviewer"  # 评审者
    CONTRIBUTOR = "contributor"  # 贡献者
    OBSERVER = "observer"  # 观察者
    MODERATOR = "moderator"  # 主持人


@dataclass
class TeamMember:
    """团队成员信息"""
    agent: UniversalAgent
    role: CollaborationRole
    capabilities: List[AgentCapability]
    priority: int = 0
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    joined_at: datetime = field(default_factory=datetime.now)


@dataclass
class CollaborationTask:
    """协作任务"""
    task_id: str
    original_task: UniversalTask
    pattern: CollaborationPattern
    assigned_members: List[str] = field(default_factory=list)
    results: Dict[str, UniversalResult] = field(default_factory=dict)
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationResult:
    """协作结果"""
    task_id: str
    pattern: CollaborationPattern
    final_result: UniversalResult
    individual_results: Dict[str, UniversalResult]
    consensus_score: float = 0.0
    collaboration_metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class CollaborationManager:
    """
    团队协作管理器
    
    实现多种协作模式的Agent团队协作
    """
    
    def __init__(self):
        self.teams: Dict[str, Dict[str, TeamMember]] = {}
        self.active_collaborations: Dict[str, CollaborationTask] = {}
        self.collaboration_history: List[CollaborationResult] = []
        self.pattern_handlers: Dict[CollaborationPattern, Callable] = {
            CollaborationPattern.SEQUENTIAL: self._handle_sequential,
            CollaborationPattern.PARALLEL: self._handle_parallel,
            CollaborationPattern.ROUND_ROBIN: self._handle_round_robin,
            CollaborationPattern.EXPERT_CONSULTATION: self._handle_expert_consultation,
            CollaborationPattern.PEER_REVIEW: self._handle_peer_review,
            CollaborationPattern.DEBATE: self._handle_debate,
            CollaborationPattern.CONSENSUS: self._handle_consensus,
            CollaborationPattern.HIERARCHICAL: self._handle_hierarchical,
        }
    
    async def create_team(self, team_id: str, members: List[TeamMember] = None) -> bool:
        """创建新团队"""
        if team_id not in self.teams:
            self.teams[team_id] = {}
            logger.info(f"Created new team: {team_id}")
            
            # 添加成员
            if members:
                for member in members:
                    self.teams[team_id][member.agent.agent_id] = member
                logger.info(f"Added {len(members)} members to team: {team_id}")
            
            return True
        else:
            logger.warning(f"Team {team_id} already exists")
            return False
    
    async def add_team_member(self, 
                       team_id: str, 
                       member_id: str,
                       agent: UniversalAgent, 
                       role: CollaborationRole = CollaborationRole.CONTRIBUTOR,
                       priority: int = 0) -> bool:
        """添加团队成员"""
        if team_id not in self.teams:
            await self.create_team(team_id)
        
        member = TeamMember(
            agent=agent,
            role=role,
            capabilities=agent.get_capabilities(),
            priority=priority
        )
        
        self.teams[team_id][member_id] = member
        logger.info(f"Added member {member_id} to team {team_id} with role {role.value}")
        return True
    
    def remove_team_member(self, team_id: str, member_id: str) -> bool:
        """移除团队成员"""
        if team_id in self.teams and member_id in self.teams[team_id]:
            del self.teams[team_id][member_id]
            logger.info(f"Removed member {member_id} from team {team_id}")
            return True
        return False
    
    def get_team_members(self, team_id: str) -> Dict[str, TeamMember]:
        """获取团队成员"""
        return self.teams.get(team_id, {})
    
    async def collaborate(self, 
                         team_id: str,
                         task: UniversalTask,
                         pattern: CollaborationPattern,
                         context: Optional[UniversalContext] = None,
                         config: Optional[Dict[str, Any]] = None,
                         member_filter: Optional[Callable[[TeamMember], bool]] = None) -> CollaborationResult:
        """协作方法 - execute_collaboration的别名，提供更简洁的接口"""
        return await self.execute_collaboration(team_id, task, pattern, context, member_filter)
    
    async def execute_collaboration(self, 
                                  team_id: str,
                                  task: UniversalTask,
                                  pattern: CollaborationPattern,
                                  context: Optional[UniversalContext] = None,
                                  member_filter: Optional[Callable[[TeamMember], bool]] = None) -> CollaborationResult:
        """执行团队协作任务"""
        
        if team_id not in self.teams:
            raise ValueError(f"Team {team_id} not found")
        
        # 创建协作任务
        collaboration_task = CollaborationTask(
            task_id=str(uuid.uuid4()),
            original_task=task,
            pattern=pattern
        )
        
        # 选择参与协作的成员
        available_members = self.teams[team_id]
        if member_filter:
            available_members = {
                mid: member for mid, member in available_members.items()
                if member.is_active and member_filter(member)
            }
        else:
            available_members = {
                mid: member for mid, member in available_members.items()
                if member.is_active
            }
        
        if not available_members:
            raise ValueError(f"No available members in team {team_id}")
        
        collaboration_task.assigned_members = list(available_members.keys())
        self.active_collaborations[collaboration_task.task_id] = collaboration_task
        
        try:
            # 执行协作模式
            handler = self.pattern_handlers.get(pattern)
            if not handler:
                raise ValueError(f"Unsupported collaboration pattern: {pattern}")
            
            logger.info(f"Starting {pattern.value} collaboration with {len(available_members)} members")
            
            result = await handler(
                collaboration_task,
                available_members,
                context or UniversalContext()
            )
            
            # 记录协作历史
            self.collaboration_history.append(result)
            
            # 清理活跃协作
            if collaboration_task.task_id in self.active_collaborations:
                del self.active_collaborations[collaboration_task.task_id]
            
            logger.info(f"Completed {pattern.value} collaboration with consensus score: {result.consensus_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Collaboration failed: {e}")
            
            # 创建错误结果
            error_result = UniversalResult(
                content=f"Collaboration failed: {str(e)}",
                status=ResultStatus.ERROR
            )
            
            return CollaborationResult(
                task_id=collaboration_task.task_id,
                pattern=pattern,
                final_result=error_result,
                individual_results={},
                consensus_score=0.0
            )
    
    async def _handle_sequential(self, 
                               task: CollaborationTask,
                               members: Dict[str, TeamMember],
                               context: UniversalContext) -> CollaborationResult:
        """处理顺序执行模式"""
        results = {}
        current_context = context.copy() if hasattr(context, 'copy') else UniversalContext()
        
        # 按优先级排序成员
        sorted_members = sorted(members.items(), key=lambda x: x[1].priority, reverse=True)
        
        for member_id, member in sorted_members:
            try:
                # 执行任务
                result = await member.agent.execute(task.original_task, current_context)
                results[member_id] = result
                
                # 更新上下文，传递给下一个成员
                if result.is_successful():
                    current_context.set(f"previous_result_{member_id}", result.content)
                    current_context.set("last_successful_member", member_id)
                
            except Exception as e:
                logger.error(f"Member {member_id} failed: {e}")
                results[member_id] = UniversalResult(
                    content=f"Execution failed: {str(e)}",
                    status=ResultStatus.ERROR
                )
        
        # 选择最后一个成功的结果作为最终结果
        final_result = None
        for member_id, result in reversed(results.items()):
            if result.is_successful():
                final_result = result
                break
        
        if not final_result:
            final_result = UniversalResult(
                content="All members failed to execute the task",
                status=ResultStatus.ERROR
            )
        
        return CollaborationResult(
            task_id=task.task_id,
            pattern=CollaborationPattern.SEQUENTIAL,
            final_result=final_result,
            individual_results=results,
            consensus_score=self._calculate_consensus_score(results)
        )
    
    async def _handle_parallel(self, 
                             task: CollaborationTask,
                             members: Dict[str, TeamMember],
                             context: UniversalContext) -> CollaborationResult:
        """处理并行执行模式"""
        # 并行执行所有成员的任务
        tasks = []
        member_ids = []
        
        for member_id, member in members.items():
            member_context = context.copy() if hasattr(context, 'copy') else UniversalContext()
            member_context.set("member_id", member_id)
            member_context.set("member_role", member.role.value)
            
            task_coroutine = member.agent.execute(task.original_task, member_context)
            tasks.append(task_coroutine)
            member_ids.append(member_id)
        
        # 等待所有任务完成
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        results = {}
        for member_id, result in zip(member_ids, results_list):
            if isinstance(result, Exception):
                results[member_id] = UniversalResult(
                    content=f"Execution failed: {str(result)}",
                    status=ResultStatus.ERROR
                )
            else:
                results[member_id] = result
        
        # 聚合结果
        final_result = self._aggregate_parallel_results(results)
        
        return CollaborationResult(
            task_id=task.task_id,
            pattern=CollaborationPattern.PARALLEL,
            final_result=final_result,
            individual_results=results,
            consensus_score=self._calculate_consensus_score(results)
        )
    
    async def _handle_round_robin(self, 
                                task: CollaborationTask,
                                members: Dict[str, TeamMember],
                                context: UniversalContext) -> CollaborationResult:
        """处理轮询执行模式"""
        results = {}
        conversation_history = []
        
        # 轮询执行，每个成员基于前面的结果继续
        member_list = list(members.items())
        rounds = min(3, len(member_list))  # 最多3轮
        
        for round_num in range(rounds):
            for i, (member_id, member) in enumerate(member_list):
                # 构建包含对话历史的上下文
                round_context = context.copy() if hasattr(context, 'copy') else UniversalContext()
                round_context.set("conversation_history", conversation_history)
                round_context.set("round", round_num + 1)
                round_context.set("member_position", i + 1)
                
                try:
                    result = await member.agent.execute(task.original_task, round_context)
                    results[f"{member_id}_round_{round_num}"] = result
                    
                    # 添加到对话历史
                    if result.is_successful():
                        conversation_history.append({
                            "member_id": member_id,
                            "round": round_num + 1,
                            "content": result.content,
                            "role": member.role.value
                        })
                
                except Exception as e:
                    logger.error(f"Round robin member {member_id} failed: {e}")
                    results[f"{member_id}_round_{round_num}"] = UniversalResult(
                        content=f"Execution failed: {str(e)}",
                        status=ResultStatus.ERROR
                    )
        
        # 选择最后一轮的最佳结果
        final_result = self._select_best_round_robin_result(results, conversation_history)
        
        return CollaborationResult(
            task_id=task.task_id,
            pattern=CollaborationPattern.ROUND_ROBIN,
            final_result=final_result,
            individual_results=results,
            consensus_score=self._calculate_consensus_score(results),
            collaboration_metrics={
                "rounds": rounds,
                "total_exchanges": len(conversation_history)
            }
        )
    
    async def _handle_expert_consultation(self, 
                                        task: CollaborationTask,
                                        members: Dict[str, TeamMember],
                                        context: UniversalContext) -> CollaborationResult:
        """处理专家会诊模式"""
        # 找出专家和领导者
        experts = {mid: member for mid, member in members.items() 
                  if member.role in [CollaborationRole.EXPERT, CollaborationRole.LEADER]}
        
        if not experts:
            # 如果没有专家，按能力选择
            experts = dict(list(members.items())[:3])  # 选择前3个成员
        
        results = {}
        expert_opinions = []
        
        # 专家并行提供意见
        expert_tasks = []
        expert_ids = []
        
        for expert_id, expert in experts.items():
            expert_context = context.copy() if hasattr(context, 'copy') else UniversalContext()
            expert_context.set("consultation_mode", True)
            expert_context.set("expert_role", expert.role.value)
            
            task_coroutine = expert.agent.execute(task.original_task, expert_context)
            expert_tasks.append(task_coroutine)
            expert_ids.append(expert_id)
        
        expert_results = await asyncio.gather(*expert_tasks, return_exceptions=True)
        
        # 收集专家意见
        for expert_id, result in zip(expert_ids, expert_results):
            if isinstance(result, Exception):
                results[expert_id] = UniversalResult(
                    content=f"Expert consultation failed: {str(result)}",
                    status=ResultStatus.ERROR
                )
            else:
                results[expert_id] = result
                if result.is_successful():
                    expert_opinions.append({
                        "expert_id": expert_id,
                        "opinion": result.content,
                        "role": experts[expert_id].role.value
                    })
        
        # 综合专家意见
        final_result = self._synthesize_expert_opinions(expert_opinions, task.original_task)
        
        return CollaborationResult(
            task_id=task.task_id,
            pattern=CollaborationPattern.EXPERT_CONSULTATION,
            final_result=final_result,
            individual_results=results,
            consensus_score=self._calculate_consensus_score(results),
            collaboration_metrics={
                "experts_consulted": len(expert_opinions),
                "expert_opinions": expert_opinions
            }
        )
    
    async def _handle_peer_review(self, 
                                task: CollaborationTask,
                                members: Dict[str, TeamMember],
                                context: UniversalContext) -> CollaborationResult:
        """处理同行评议模式"""
        if len(members) < 2:
            raise ValueError("Peer review requires at least 2 members")
        
        results = {}
        
        # 第一阶段：初始解决方案
        member_list = list(members.items())
        primary_member_id, primary_member = member_list[0]
        
        primary_context = context.copy() if hasattr(context, 'copy') else UniversalContext()
        primary_context.set("phase", "initial_solution")
        
        initial_result = await primary_member.agent.execute(task.original_task, primary_context)
        results[f"{primary_member_id}_initial"] = initial_result
        
        if not initial_result.is_successful():
            return CollaborationResult(
                task_id=task.task_id,
                pattern=CollaborationPattern.PEER_REVIEW,
                final_result=initial_result,
                individual_results=results,
                consensus_score=0.0
            )
        
        # 第二阶段：同行评议
        reviews = []
        review_tasks = []
        reviewer_ids = []
        
        for reviewer_id, reviewer in member_list[1:]:
            review_context = context.copy() if hasattr(context, 'copy') else UniversalContext()
            review_context.set("phase", "peer_review")
            review_context.set("original_solution", initial_result.content)
            review_context.set("reviewer_role", reviewer.role.value)
            
            # 创建评议任务
            review_task = UniversalTask(
                content=f"Please review and provide feedback on the following solution to: {task.original_task.content}\n\nSolution: {initial_result.content}",
                task_type=TaskType.ANALYSIS
            )
            
            task_coroutine = reviewer.agent.execute(review_task, review_context)
            review_tasks.append(task_coroutine)
            reviewer_ids.append(reviewer_id)
        
        review_results = await asyncio.gather(*review_tasks, return_exceptions=True)
        
        # 收集评议结果
        for reviewer_id, result in zip(reviewer_ids, review_results):
            if isinstance(result, Exception):
                results[f"{reviewer_id}_review"] = UniversalResult(
                    content=f"Review failed: {str(result)}",
                    status=ResultStatus.ERROR
                )
            else:
                results[f"{reviewer_id}_review"] = result
                if result.is_successful():
                    reviews.append({
                        "reviewer_id": reviewer_id,
                        "review": result.content,
                        "role": members[reviewer_id].role.value
                    })
        
        # 第三阶段：基于评议改进解决方案
        if reviews:
            improvement_context = context.copy() if hasattr(context, 'copy') else UniversalContext()
            improvement_context.set("phase", "improvement")
            improvement_context.set("original_solution", initial_result.content)
            improvement_context.set("peer_reviews", reviews)
            
            improvement_task = UniversalTask(
                content=f"Based on the peer reviews, improve your solution to: {task.original_task.content}",
                task_type=task.original_task.task_type
            )
            
            final_result = await primary_member.agent.execute(improvement_task, improvement_context)
            results[f"{primary_member_id}_improved"] = final_result
        else:
            final_result = initial_result
        
        return CollaborationResult(
            task_id=task.task_id,
            pattern=CollaborationPattern.PEER_REVIEW,
            final_result=final_result,
            individual_results=results,
            consensus_score=self._calculate_consensus_score(results),
            collaboration_metrics={
                "reviewers": len(reviews),
                "reviews": reviews
            }
        )
    
    async def _handle_debate(self, 
                           task: CollaborationTask,
                           members: Dict[str, TeamMember],
                           context: UniversalContext) -> CollaborationResult:
        """处理辩论模式"""
        if len(members) < 2:
            raise ValueError("Debate requires at least 2 members")
        
        results = {}
        debate_rounds = []
        
        member_list = list(members.items())
        rounds = min(3, len(member_list))  # 最多3轮辩论
        
        # 初始立场
        for i, (member_id, member) in enumerate(member_list[:2]):  # 只取前两个成员进行辩论
            stance_context = context.copy() if hasattr(context, 'copy') else UniversalContext()
            stance_context.set("debate_mode", True)
            stance_context.set("position", "pro" if i == 0 else "con")
            stance_context.set("round", 0)
            
            initial_task = UniversalTask(
                content=f"Present your {'supporting' if i == 0 else 'opposing'} argument for: {task.original_task.content}",
                task_type=TaskType.ANALYSIS
            )
            
            result = await member.agent.execute(initial_task, stance_context)
            results[f"{member_id}_round_0"] = result
            
            if result.is_successful():
                debate_rounds.append({
                    "member_id": member_id,
                    "position": "pro" if i == 0 else "con",
                    "round": 0,
                    "argument": result.content
                })
        
        # 辩论轮次
        for round_num in range(1, rounds):
            for i, (member_id, member) in enumerate(member_list[:2]):
                # 获取对方的论点
                opponent_args = [r["argument"] for r in debate_rounds 
                               if r["position"] != ("pro" if i == 0 else "con")]
                
                debate_context = context.copy() if hasattr(context, 'copy') else UniversalContext()
                debate_context.set("debate_mode", True)
                debate_context.set("position", "pro" if i == 0 else "con")
                debate_context.set("round", round_num)
                debate_context.set("opponent_arguments", opponent_args)
                
                counter_task = UniversalTask(
                    content=f"Counter the opposing arguments and strengthen your {'supporting' if i == 0 else 'opposing'} position on: {task.original_task.content}",
                    task_type=TaskType.ANALYSIS
                )
                
                result = await member.agent.execute(counter_task, debate_context)
                results[f"{member_id}_round_{round_num}"] = result
                
                if result.is_successful():
                    debate_rounds.append({
                        "member_id": member_id,
                        "position": "pro" if i == 0 else "con",
                        "round": round_num,
                        "argument": result.content
                    })
        
        # 选择获胜方或综合观点
        final_result = self._judge_debate(debate_rounds, task.original_task)
        
        return CollaborationResult(
            task_id=task.task_id,
            pattern=CollaborationPattern.DEBATE,
            final_result=final_result,
            individual_results=results,
            consensus_score=self._calculate_consensus_score(results),
            collaboration_metrics={
                "debate_rounds": rounds,
                "arguments_presented": len(debate_rounds)
            }
        )
    
    async def _handle_consensus(self, 
                              task: CollaborationTask,
                              members: Dict[str, TeamMember],
                              context: UniversalContext) -> CollaborationResult:
        """处理共识达成模式"""
        results = {}
        proposals = []
        
        # 第一阶段：每个成员提出解决方案
        proposal_tasks = []
        member_ids = []
        
        for member_id, member in members.items():
            proposal_context = context.copy() if hasattr(context, 'copy') else UniversalContext()
            proposal_context.set("consensus_mode", True)
            proposal_context.set("phase", "proposal")
            
            task_coroutine = member.agent.execute(task.original_task, proposal_context)
            proposal_tasks.append(task_coroutine)
            member_ids.append(member_id)
        
        proposal_results = await asyncio.gather(*proposal_tasks, return_exceptions=True)
        
        # 收集提案
        for member_id, result in zip(member_ids, proposal_results):
            if isinstance(result, Exception):
                results[f"{member_id}_proposal"] = UniversalResult(
                    content=f"Proposal failed: {str(result)}",
                    status=ResultStatus.ERROR
                )
            else:
                results[f"{member_id}_proposal"] = result
                if result.is_successful():
                    proposals.append({
                        "member_id": member_id,
                        "proposal": result.content,
                        "role": members[member_id].role.value
                    })
        
        if not proposals:
            final_result = UniversalResult(
                content="No valid proposals were generated",
                status=ResultStatus.ERROR
            )
        else:
            # 第二阶段：达成共识
            consensus_context = context.copy() if hasattr(context, 'copy') else UniversalContext()
            consensus_context.set("consensus_mode", True)
            consensus_context.set("phase", "consensus")
            consensus_context.set("all_proposals", proposals)
            
            # 选择一个成员来综合所有提案
            synthesizer_id, synthesizer = next(iter(members.items()))
            
            consensus_task = UniversalTask(
                content=f"Synthesize the following proposals into a consensus solution for: {task.original_task.content}\n\nProposals: {proposals}",
                task_type=task.original_task.task_type
            )
            
            final_result = await synthesizer.agent.execute(consensus_task, consensus_context)
            results[f"{synthesizer_id}_consensus"] = final_result
        
        return CollaborationResult(
            task_id=task.task_id,
            pattern=CollaborationPattern.CONSENSUS,
            final_result=final_result,
            individual_results=results,
            consensus_score=self._calculate_consensus_score(results),
            collaboration_metrics={
                "proposals_count": len(proposals),
                "proposals": proposals
            }
        )
    
    async def _handle_hierarchical(self, 
                                 task: CollaborationTask,
                                 members: Dict[str, TeamMember],
                                 context: UniversalContext) -> CollaborationResult:
        """处理分层决策模式"""
        results = {}
        
        # 按角色分层
        leaders = {mid: member for mid, member in members.items() 
                  if member.role == CollaborationRole.LEADER}
        experts = {mid: member for mid, member in members.items() 
                  if member.role == CollaborationRole.EXPERT}
        contributors = {mid: member for mid, member in members.items() 
                       if member.role == CollaborationRole.CONTRIBUTOR}
        
        # 第一层：贡献者提供初始输入
        contributor_inputs = []
        if contributors:
            contributor_tasks = []
            contributor_ids = []
            
            for contributor_id, contributor in contributors.items():
                contributor_context = context.copy() if hasattr(context, 'copy') else UniversalContext()
                contributor_context.set("hierarchical_mode", True)
                contributor_context.set("level", "contributor")
                
                task_coroutine = contributor.agent.execute(task.original_task, contributor_context)
                contributor_tasks.append(task_coroutine)
                contributor_ids.append(contributor_id)
            
            contributor_results = await asyncio.gather(*contributor_tasks, return_exceptions=True)
            
            for contributor_id, result in zip(contributor_ids, contributor_results):
                if isinstance(result, Exception):
                    results[f"{contributor_id}_input"] = UniversalResult(
                        content=f"Contributor input failed: {str(result)}",
                        status=ResultStatus.ERROR
                    )
                else:
                    results[f"{contributor_id}_input"] = result
                    if result.is_successful():
                        contributor_inputs.append({
                            "contributor_id": contributor_id,
                            "input": result.content
                        })
        
        # 第二层：专家分析和建议
        expert_recommendations = []
        if experts:
            expert_tasks = []
            expert_ids = []
            
            for expert_id, expert in experts.items():
                expert_context = context.copy() if hasattr(context, 'copy') else UniversalContext()
                expert_context.set("hierarchical_mode", True)
                expert_context.set("level", "expert")
                expert_context.set("contributor_inputs", contributor_inputs)
                
                expert_task = UniversalTask(
                    content=f"Based on contributor inputs, provide expert analysis for: {task.original_task.content}",
                    task_type=TaskType.ANALYSIS
                )
                
                task_coroutine = expert.agent.execute(expert_task, expert_context)
                expert_tasks.append(task_coroutine)
                expert_ids.append(expert_id)
            
            expert_results = await asyncio.gather(*expert_tasks, return_exceptions=True)
            
            for expert_id, result in zip(expert_ids, expert_results):
                if isinstance(result, Exception):
                    results[f"{expert_id}_analysis"] = UniversalResult(
                        content=f"Expert analysis failed: {str(result)}",
                        status=ResultStatus.ERROR
                    )
                else:
                    results[f"{expert_id}_analysis"] = result
                    if result.is_successful():
                        expert_recommendations.append({
                            "expert_id": expert_id,
                            "recommendation": result.content
                        })
        
        # 第三层：领导者最终决策
        if leaders:
            leader_id, leader = next(iter(leaders.items()))
            
            decision_context = context.copy() if hasattr(context, 'copy') else UniversalContext()
            decision_context.set("hierarchical_mode", True)
            decision_context.set("level", "leader")
            decision_context.set("contributor_inputs", contributor_inputs)
            decision_context.set("expert_recommendations", expert_recommendations)
            
            decision_task = UniversalTask(
                content=f"Make final decision based on team inputs for: {task.original_task.content}",
                task_type=task.original_task.task_type
            )
            
            final_result = await leader.agent.execute(decision_task, decision_context)
            results[f"{leader_id}_decision"] = final_result
        else:
            # 如果没有领导者，综合专家建议
            if expert_recommendations:
                final_result = UniversalResult(
                    content=f"Expert consensus: {expert_recommendations}",
                    status=ResultStatus.SUCCESS
                )
            else:
                final_result = UniversalResult(
                    content="No leadership or expert guidance available",
                    status=ResultStatus.ERROR
                )
        
        return CollaborationResult(
            task_id=task.task_id,
            pattern=CollaborationPattern.HIERARCHICAL,
            final_result=final_result,
            individual_results=results,
            consensus_score=self._calculate_consensus_score(results),
            collaboration_metrics={
                "contributors": len(contributor_inputs),
                "experts": len(expert_recommendations),
                "leaders": len(leaders)
            }
        )
    
    def _calculate_consensus_score(self, results: Dict[str, UniversalResult]) -> float:
        """计算共识分数"""
        if not results:
            return 0.0
        
        successful_results = [r for r in results.values() if r.is_successful()]
        if not successful_results:
            return 0.0
        
        # 简单的共识分数计算：成功率
        return len(successful_results) / len(results)
    
    def _aggregate_parallel_results(self, results: Dict[str, UniversalResult]) -> UniversalResult:
        """聚合并行执行结果"""
        successful_results = [r for r in results.values() if r.is_successful()]
        
        if not successful_results:
            return UniversalResult(
                content="All parallel executions failed",
                status=ResultStatus.ERROR
            )
        
        # 简单聚合：选择第一个成功的结果，或者组合所有结果
        if len(successful_results) == 1:
            return successful_results[0]
        
        # 组合多个结果
        combined_content = {
            "aggregated_results": [r.content for r in successful_results],
            "summary": f"Combined results from {len(successful_results)} agents"
        }
        
        return UniversalResult(
            content=combined_content,
            status=ResultStatus.SUCCESS
        )
    
    def _select_best_round_robin_result(self, 
                                      results: Dict[str, UniversalResult],
                                      conversation_history: List[Dict[str, Any]]) -> UniversalResult:
        """选择轮询执行的最佳结果"""
        if not conversation_history:
            return UniversalResult(
                content="No successful round robin exchanges",
                status=ResultStatus.ERROR
            )
        
        # 选择最后一轮的结果
        last_exchange = conversation_history[-1]
        
        return UniversalResult(
            content={
                "final_response": last_exchange["content"],
                "conversation_summary": f"Round robin completed with {len(conversation_history)} exchanges",
                "full_conversation": conversation_history
            },
            status=ResultStatus.SUCCESS
        )
    
    def _synthesize_expert_opinions(self, 
                                  opinions: List[Dict[str, Any]],
                                  original_task: UniversalTask) -> UniversalResult:
        """综合专家意见"""
        if not opinions:
            return UniversalResult(
                content="No expert opinions available",
                status=ResultStatus.ERROR
            )
        
        synthesis = {
            "expert_count": len(opinions),
            "opinions": opinions,
            "synthesis": f"Based on {len(opinions)} expert consultations, the recommended approach is synthesized from multiple perspectives."
        }
        
        return UniversalResult(
            content=synthesis,
            status=ResultStatus.SUCCESS
        )
    
    def _judge_debate(self, 
                     debate_rounds: List[Dict[str, Any]],
                     original_task: UniversalTask) -> UniversalResult:
        """评判辩论结果"""
        if not debate_rounds:
            return UniversalResult(
                content="No debate arguments presented",
                status=ResultStatus.ERROR
            )
        
        # 简单评判：综合双方观点
        pro_args = [r["argument"] for r in debate_rounds if r["position"] == "pro"]
        con_args = [r["argument"] for r in debate_rounds if r["position"] == "con"]
        
        judgment = {
            "debate_summary": f"Debate completed with {len(debate_rounds)} arguments",
            "pro_arguments": pro_args,
            "con_arguments": con_args,
            "balanced_conclusion": "Both perspectives have been considered in reaching a balanced conclusion."
        }
        
        return UniversalResult(
            content=judgment,
            status=ResultStatus.SUCCESS
        )
    
    def get_collaboration_history(self, limit: int = 10) -> List[CollaborationResult]:
        """获取协作历史"""
        return self.collaboration_history[-limit:]
    
    def get_active_collaborations(self) -> Dict[str, CollaborationTask]:
        """获取活跃的协作任务"""
        return self.active_collaborations.copy()
    
    def get_team_statistics(self, team_id: str) -> Dict[str, Any]:
        """获取团队统计信息"""
        if team_id not in self.teams:
            return {}
        
        members = self.teams[team_id]
        
        return {
            "team_id": team_id,
            "member_count": len(members),
            "active_members": len([m for m in members.values() if m.is_active]),
            "role_distribution": {
                role.value: len([m for m in members.values() if m.role == role])
                for role in CollaborationRole
            },
            "capability_coverage": list(set(
                cap for member in members.values() 
                for cap in member.capabilities
            ))
        } 