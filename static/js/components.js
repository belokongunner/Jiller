const USER = 'phobos';
const USER_ID = 1;
const ROOM = document.querySelector('body').dataset['room'];

let userList = [];
let issueList = [];
let chatLog = [];
let currentIssue = 0;

/*
if (location.pathname.substr(1,4) === 'room') {
    //ROOM = location.pathname.replace(/^\/room\/|\/$/g, '')
}
*/
let socket = io.connect('http://127.0.0.1:5000');
socket.on('connect', () => socket.send('User has connected!') );

socket.on('start_data', (data) => {
    userList = data.user_list;
    issueList = data.issue_list;
    chatLog = data.chat_log;
    //console.log('Комменты: ', chatLog);






/*
var socket = io.connect('http://localhost');
socket.on('news', function (data) {
  console.log(data);
  socket.emit('my other event', { my: 'data' });
});


$(document).ready(function() {
	var socket = io.connect('http://127.0.0.1:5000');
	socket.on('connect', function() {
		socket.send('User has connected!');
	});
	socket.on('message', function(msg) {
		$("#messages").append('<li>'+msg+'</li>');
		console.log('Received message');
	});
	$('#sendbutton').on('click', function() {
		socket.send($('#myMessage').val());
		$('#myMessage').val('');
	});
});

*/


let cardList = [0, 1, 2, 3, 5, 8, 13, 20, 40, 100, '?', 'coffee'];
// auto
let status = {
    'flip': true,

};


class PokerBox extends React.Component {
    render() {
        return (
            <div>
                <h3>Jiller planning poker service
                    <div className="profile">{USER}</div>
                </h3>
                <IssueBox />
                <UserBox />
                <CommentBox />
            </div>
        );
    }
}


class UserBox extends React.Component {
    constructor() {
        super();
        this.state = {
            'userList': userList,
            'flip': false
        }
    }
    componentWillMount() {
        this._changeUserStatus();
    }
    render() {
        const users = this._getUsers();
        /*<h4 className="user-count">{ userList.filter(x => x.online).length }
                    user online</h4>*/

        return (
            <div className="user-box col-md-3 col-sm-2 pull-right">
                <div className="user-list info info-striped">
                    <div className="info-row">
                        <div className="col-md-8 info-name">Nickname</div>
                        <div className="col-md-4 info-value">Vote</div>
                    </div>
                    { users }
                </div>
            </div> );
    }

    _getUsers() {
        return (this.state.userList.map(user => {
                return <User name={user.name} role={user.role} vote={user.current_vote}
                             key={user.id} flip={this.state.flip} />
            })
        )
    };

    _changeUserStatus() {
        socket.on('make_vote', newUserList => {
            console.log(newUserList);
            this.setState({userList: newUserList});
            if (newUserList.filter(x => x.current_vote).length == newUserList.length) {
                this.setState({'flip': true});
            }
        });
    }
}

class User extends React.Component {
    render() {
        let ok = <span className="glyphicon glyphicon-ok" aria-hidden="true"></span>;
        let coffee = <i className="fa fa-coffee fa-2x" aria-hidden="true"></i>;
        return (
            <div className="info-row">
                <div className="col-md-8 info-name">{this.props.name}</div>
                <div className="col-md-4 info-value">{this.props.vote === 'coffee' ? coffee: this.props.flip ? this.props.vote: this.props.vote? ok: '' }</div>
            </div> );
    }
}


class IssueBox extends React.Component {
    constructor() {
        super();
        this.state = {
            'currentSlide': 'active',
            'issueList': issueList
        };
    }


    render() {
        if (this.state.currentSlide == 'active') {
        //current issue slide
            return (
                <div className="main-block col-md-9">
                    <div className="info info-striped">
                        <div className="info-row">
                            <div className="info-name">Issue on estimation:</div>
                            <div className="info-value">{this.state.issueList[currentIssue].title}</div>
                        </div>
                        <div className="info-row">
                            <div className="info-name">Description:</div>
                            <div className="info-value">{this.state.issueList[currentIssue].description}</div>
                        </div>
                    </div>
                    <div className="info-striped">
                        <CardBox />
                        <IssueNavbar activeSlide = {this.state.currentSlide} setSlide={this._setSlide.bind(this)} />
                    </div>
                </div>
            );
        }
        if (this.state.currentSlide == 'accept') {
        //current issue slide
            return (
                <div className="main-block col-md-9">
                    <div className="info info-striped">
                        <div className="info-row">
                            <div className="info-name">Issue on estimation:</div>
                            <div className="info-value">{this.state.issueList[currentIssue].title}</div>
                        </div>
                        <div className="info-row">
                            <div className="info-name">Description:</div>
                            <div className="info-value">{this.state.issueList[currentIssue].description}</div>
                        </div>
                    </div>
                    <div className="info-striped">
                        <CardBox />
                        <IssueNavbar activeSlide = {this.state.currentSlide} setSlide={this._setSlide.bind(this)} />
                    </div>

                </div>
            );

        }
        if (this.state.currentSlide == 'completed') {
        //current issue slide
            return (
                <div className="main-block col-md-9">
                    <div className="info info-striped">
                        <div className="info-row">
                            <div className="info-name">Issue on estimation:</div>
                            <div className="info-value">{this.state.issueList[currentIssue].title}</div>
                        </div>
                        <div className="info-row">
                            <div className="info-name">Description:</div>
                            <div className="info-value">{this.state.issueList[currentIssue].description}</div>
                        </div>
                    </div>
                    <div className="info-striped">
                        <CardBox />
                        <IssueNavbar activeSlide = {this.state.currentSlide} setSlide={this._setSlide.bind(this)} />
                    </div>

                </div>
            );
        }
        if (this.state.currentSlide == 'all') {
        //current issue slide
            return (
                <div className="main-block col-md-9">
                    <div className="info info-striped">
                        <div className="info-row">
                            <div className="info-name">Issue on estimation:</div>
                            <div className="info-value">{this.state.issueList[currentIssue].title}</div>
                        </div>
                        <div className="info-row">
                            <div className="info-name">Description:</div>
                            <div className="info-value">{this.state.issueList[currentIssue].description}</div>
                        </div>
                    </div>
                    <div className="info-striped">
                        <CardBox />
                        <IssueNavbar activeSlide={this.state.currentSlide} setSlide={this._setSlide.bind(this)} />
                    </div>
                </div>
            );
        }
    }

    _setSlide(slide) {
        this.setState({'currentSlide': slide});
    }
}


class CardBox extends React.Component {
    constructor() {
        super();
        this.state = {
            'chosenCard': null,
        };
    }

    render() {
        let coffee = <i className="fa fa-coffee" aria-hidden="true"></i>;
        return (<div>
            {
                cardList.map((card, index) => {
                    return <div className={this.state.chosenCard == card ? 'chosen card': 'card'}
                                data-card={card} key={index} onClick={this._sendEstimation.bind(this)}>
                        <div className="card-top-data">{card}</div>
                        <div className="card-center-data">{card =='coffee'? coffee: card}</div>
                        <div className="card-bottom-data">{card}</div>
                    </div>
                })
            }
        </div>)
    }

    _sendEstimation(event) {
        let card = event.currentTarget.dataset['card'];
        this.setState({chosenCard: card});
        socket.emit('make_vote', {'user_id': USER_ID, 'card': card});
    }

}

class IssueNavbar extends React.Component {
    render() {
        return (
            <div className="issue-bar">
                <button className={this._checkActiveBtn('active')} onClick = {this.props.setSlide.bind(this, 'active')}>Active issue</button>
                <button className={this._checkActiveBtn('accept')} onClick = {this.props.setSlide.bind(this, 'accept')}>Accept vote</button>
                <button className={this._checkActiveBtn('completed')} onClick = {this.props.setSlide.bind(this, 'completed')}>Completed issue</button>
                <button className={this._checkActiveBtn('all')} onClick = {this.props.setSlide.bind(this, 'all')}>All issue list</button>
            </div>
        )
    }
     _checkActiveBtn(slide) {
        console.log(slide, this.props.activeSlide);
        return (slide == this.props.activeSlide) ? "btn btn-info" : "btn";
    }
}


class CommentBox extends React.Component {

    constructor() {
        super();
        this.state = {
            'comments': chatLog
        };
    };
    componentWillMount() {
        this._addNewComment();
    }

    render() {

        let comments = this._getComments();
        return (
            <div className="col-md-12 col-sm-10">
                <CommentForm addComment={this._sendComment.bind(this)}/>
                <div className="comment-box"> { comments } </div>
            </div>
        );
    }

    _addNewComment() {
        socket.on('add_new_comment', newComment => {
            this.setState({comments: this.state.comments.concat([newComment])});
        });
    }

    _sendComment(user, body) {
        const comment = {
            id: this.state.comments.length + 1,
            user,
            body
        };
        socket.emit('add_comment', comment);
    }

    _getComments() {
        return this.state.comments.map(comment => {
            return (
                <Comment
                    user={comment.user}
                    body={comment.body}
                    key={comment.id} />
            );
        });
    };

}


class CommentForm extends React.Component {
    render() {
        return (
            <form onSubmit={this._handleSubmit.bind(this)}>
                <div className="input-group">
                    <input className="form-control form-group" placeholder="Type your comment there" ref={(input) => this._body = input} />
                        <div className="input-group-btn">
                            <button className="btn btn-info no-radius" type="submit">Post comment <i className="glyphicon glyphicon-share-alt"></i>
                            </button>
                        </div>
                </div>
            </form>
        );
    }

    _handleSubmit(event) {
        event.preventDefault();
        let body = this._body.value;
        if (body) {
            this.props.addComment(USER, body);
        this._body.value = '';
        }

    }
}


class Comment extends React.Component {
    render() {
        return (
            <div className="comment">
                <p>{this.props.user}</p>
                <p>{this.props.body}</p>
            </div> );
    }
}


ReactDOM.render(
    <PokerBox />, document.getElementById('poker-app')
);

});