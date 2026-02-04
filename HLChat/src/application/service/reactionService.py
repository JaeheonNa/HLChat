from typing import Dict, List

from fastapi import Depends
from typing_extensions import override

from adapter.output.reactionPersistenceAdapter import RequestReactionPersistenceAdapter
from adapter.output.redisStreamProducer import RedisStreamProducer
from application.port.input.reactionUsecase import (
    ToggleReactionUsecase,
    FindReactionsByMessageUsecase,
    FindReactionsByRoomUsecase
)
from application.port.output.messagePort import RedisPublishMessagePort
from application.port.output.reactionPort import MongoReactionPort
from domain.odm import HLChatReaction
from domain.reactionRequest import ToggleReactionRequest


def _build_reactions_dict(reactions: List[HLChatReaction]) -> Dict:
    """반응 목록을 { reaction_type: { count, users } } 형태로 변환"""
    result = {}
    for reaction in reactions:
        if reaction.reaction_type not in result:
            result[reaction.reaction_type] = {
                "count": 0,
                "users": []
            }
        result[reaction.reaction_type]["count"] += 1
        result[reaction.reaction_type]["users"].append({
            "userId": reaction.user_id,
            "userName": reaction.user_name
        })
    return result


class ToggleReactionService(ToggleReactionUsecase):
    def __init__(
        self,
        mongoReactionPort: MongoReactionPort = Depends(RequestReactionPersistenceAdapter),
        redisMessagePort: RedisPublishMessagePort = Depends(RedisStreamProducer)
    ):
        self.mongoReactionPort = mongoReactionPort
        self.redisMessagePort = redisMessagePort

    @override
    async def toggleReaction(self, request: ToggleReactionRequest) -> Dict:
        print(f"[ReactionService] toggleReaction 요청: {request}")

        # 기존 반응 확인
        existing = await self.mongoReactionPort.findReaction(
            request.room_id,
            request.message_ln_no,
            request.reaction_type,
            request.user_id
        )
        print(f"[ReactionService] 기존 반응: {existing}")

        if existing:
            # 반응 제거
            await self.mongoReactionPort.deleteReaction(existing)
            action = "removed"
            print(f"[ReactionService] 반응 제거됨")
        else:
            # 반응 추가
            await self.mongoReactionPort.saveReaction(request)
            action = "added"
            print(f"[ReactionService] 반응 추가됨")

        # 해당 메시지의 현재 반응 상태 조회
        reactions = await self.mongoReactionPort.findReactionsByMessage(
            request.room_id,
            request.message_ln_no
        )
        print(f"[ReactionService] 현재 반응 목록: {reactions}")
        reactions_dict = _build_reactions_dict(reactions)
        print(f"[ReactionService] 반응 dict: {reactions_dict}")

        # Redis를 통해 실시간 전파
        await self.redisMessagePort.publishMessage(
            str(request.room_id),
            {
                "type": "reaction",
                "messageLnNo": request.message_ln_no,
                "reactionType": request.reaction_type,
                "userId": request.user_id,
                "userName": request.user_name,
                "action": action,
                "reactions": reactions_dict
            }
        )

        return {
            "action": action,
            "reactions": reactions_dict
        }


class FindReactionsByMessageService(FindReactionsByMessageUsecase):
    def __init__(
        self,
        mongoReactionPort: MongoReactionPort = Depends(RequestReactionPersistenceAdapter)
    ):
        self.mongoReactionPort = mongoReactionPort

    @override
    async def findReactionsByMessage(self, room_id: int, message_ln_no: int) -> Dict:
        reactions = await self.mongoReactionPort.findReactionsByMessage(room_id, message_ln_no)
        return _build_reactions_dict(reactions)


class FindReactionsByRoomService(FindReactionsByRoomUsecase):
    def __init__(
        self,
        mongoReactionPort: MongoReactionPort = Depends(RequestReactionPersistenceAdapter)
    ):
        self.mongoReactionPort = mongoReactionPort

    @override
    async def findReactionsByRoom(self, room_id: int) -> Dict[int, Dict]:
        print(f"[ReactionService] findReactionsByRoom 요청: room_id={room_id}")
        reactions = await self.mongoReactionPort.findReactionsByRoom(room_id)
        print(f"[ReactionService] findReactionsByRoom 결과: {len(reactions)}개")

        # message_ln_no별로 그룹화
        result = {}
        for reaction in reactions:
            if reaction.message_ln_no not in result:
                result[reaction.message_ln_no] = {}

            if reaction.reaction_type not in result[reaction.message_ln_no]:
                result[reaction.message_ln_no][reaction.reaction_type] = {
                    "count": 0,
                    "users": []
                }

            result[reaction.message_ln_no][reaction.reaction_type]["count"] += 1
            result[reaction.message_ln_no][reaction.reaction_type]["users"].append({
                "userId": reaction.user_id,
                "userName": reaction.user_name
            })

        return result
